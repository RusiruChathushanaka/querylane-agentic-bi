import asyncio
import contextlib
import json
import logging
import uuid

from google.genai.errors import APIError
from pydantic import ValidationError

from app.chart_presentation import normalized_spec
from app.connectors import json_rows
from app.errors import AppError, StaleLease
from app.fusion import fuse
from app.model_selection import active_text_model, model_evidence
from app.models import Answer, ResultArtifact, VisualizationSpec
from app.repository import active_lease, now_iso
from app.skills import Skills, skill_reference

logger = logging.getLogger(__name__)


class AnalysisService:
    def __init__(self, repository, connectors, ai, settings):
        self.repo, self.connectors, self.ai, self.settings = repository, connectors, ai, settings
        self.tasks: dict[str, asyncio.Task] = {}
        self.fusion_slots = asyncio.Semaphore(1)
        self.skills = Skills(repository, settings)

    async def start(self, conversation_id, guest_id, question, key, model=None):
        run, created = await self.repo.begin(conversation_id, guest_id, question, key, model=model)
        if created:
            self.tasks[run["id"]] = asyncio.create_task(self.work(run), name=f"analysis-{run['id']}")
        return run

    async def heartbeat(self, lease):
        while True:
            await asyncio.sleep(10)
            await self.repo.renew(lease)

    async def work(self, run):
        lease = {
            "run_id": run["id"],
            "conversation_id": run["conversation_id"],
            "generation": run["generation"],
        }
        token = active_lease.set(lease)
        heartbeat = asyncio.create_task(self.heartbeat(lease))
        analysis = asyncio.create_task(
            asyncio.wait_for(
                self.execute(run["question"], run["conversation_id"]),
                timeout=self.settings.analysis_timeout_seconds,
            )
        )
        status = "complete"
        try:
            done, _ = await asyncio.wait([analysis, heartbeat], return_when=asyncio.FIRST_COMPLETED)
            if heartbeat in done:
                heartbeat.result()
            await analysis
            await self.repo.emit("complete", {"run_id": run["id"]})
        except (asyncio.CancelledError, AppError) as exc:
            code = exc.code if isinstance(exc, AppError) else "cancelled"
            status = "cancelled" if code == "cancelled" else "failed"
            if not isinstance(exc, StaleLease):
                with contextlib.suppress(AppError):
                    await self.repo.emit(
                        "error", {"code": code, "message": str(exc) or "Analysis cancelled."}
                    )
        except TimeoutError:
            status = "failed"
            with contextlib.suppress(AppError):
                await self.repo.emit(
                    "error",
                    {
                        "code": "analysis_timeout",
                        "message": "Analysis exceeded its time budget. Try a narrower question.",
                    },
                )
        except Exception:
            status = "failed"
            logger.exception("Analysis failed", extra={"run_id": run["id"]})
            with contextlib.suppress(AppError):
                await self.repo.emit(
                    "error",
                    {
                        "code": "analysis_failed",
                        "message": "Analysis could not finish. Check the source or model configuration, then try again.",
                    },
                )
        finally:
            analysis.cancel()
            heartbeat.cancel()
            await asyncio.gather(analysis, heartbeat, return_exceptions=True)
            try:
                if status != "complete":
                    try:
                        await self.connectors.cancel(run["id"])
                    except Exception:
                        logger.error("Query cancellation could not be confirmed run_id=%s", run["id"])
                try:
                    await self.repo.finish(status)
                except Exception:
                    logger.error("Analysis finalization unavailable run_id=%s; lease will expire", run["id"])
            finally:
                self.connectors.forget(run["id"])
                active_lease.reset(token)
                self.tasks.pop(run["id"], None)

    async def execute(self, question: str, conversation_id: str):
        lease = active_lease.get()
        run = await self.repo.store.get("runs", lease["run_id"])
        selected = (run or {}).get("text_model", self.settings.text_model)
        token = active_text_model.set(selected)
        try:
            return await self._execute(question, conversation_id)
        finally:
            active_text_model.reset(token)

    async def _execute(self, question: str, conversation_id: str):
        await self.connectors.ensure_data_ready()
        lease = active_lease.get()
        conversation = await self.repo.conversation(conversation_id)
        history = await self.repo.messages(conversation_id)
        analysis_id = uuid.uuid4().hex
        run = await self.repo.store.get("runs", lease["run_id"])
        await self.repo.emit("progress", {"stage": "skills", "message": "Finding relevant skills"})
        skills, skill_warnings = await self.skills.select(
            question,
            history,
            conversation["source"],
            (run or {}).get("skill_ids", conversation.get("skill_ids", [])),
            self.ai,
            analysis_id,
        )
        skills_used = [skill_reference(s, s["mode"]) for s in skills]
        await self.repo.write(
            f"runs/{lease['run_id']}/skill_snapshots",
            analysis_id,
            {
                "id": analysis_id,
                "skills": skills,
                "warnings": skill_warnings,
                "created_at": now_iso(),
            },
        )
        await self.repo.emit(
            "skills", {"skills_used": skills_used, "warnings": skill_warnings, "analysis_id": analysis_id}
        )
        await self.repo.emit(
            "progress", {"stage": "schema", "message": "Inspecting sources and business context"}
        )
        plan, retrieval = await self.ai.plan(
            question, history, conversation["source"], conversation_id, skills=skills, analysis_id=analysis_id
        )
        if plan.clarification or not plan.queries:
            message = plan.clarification or "This question needs a more specific metric or data source."
            await self.save_message(
                conversation_id, "assistant", message, skills_used=skills_used, skill_warnings=skill_warnings
            )
            await self.repo.emit("answer", {"text": message, "followups": []})
            return {"explanation": message, "skills_used": skills_used, "skill_warnings": skill_warnings}
        results = []
        for index, query in enumerate(plan.queries):
            for attempt in range(3):
                await self.repo.emit(
                    "progress",
                    {
                        "stage": "query",
                        "message": f"Running a read-only {query.source} query",
                        "source": query.source,
                    },
                )
                await self.repo.write(
                    f"runs/{lease['run_id']}/queries",
                    f"{analysis_id}_{index}_{attempt}",
                    {
                        "source": query.source,
                        "sql": query.sql,
                        "analysis_id": analysis_id,
                        "job_id": f"abi_{lease['run_id']}_{analysis_id}_{index + attempt * 2}"
                        if query.source == "bigquery"
                        else None,
                    },
                )
                try:
                    result = await self.connectors.query(
                        query.source, query.sql, lease["run_id"], f"{analysis_id}_{index + attempt * 2}"
                    )
                    results.append(result)
                    break
                except AppError as exc:
                    if (
                        plan.metric_snapshots
                        or exc.code not in ("invalid_sql", "unsafe_sql")
                        or attempt == 2
                        or self.settings.ai_backend != "gemini"
                    ):
                        raise
                    repaired, _ = await self.ai.plan(
                        question,
                        history,
                        conversation["source"],
                        conversation_id,
                        feedback=str(exc),
                        skills=skills,
                        analysis_id=analysis_id,
                    )
                    if (
                        len(repaired.queries) != len(plan.queries)
                        or repaired.queries[index].source != query.source
                        or repaired.queries[:index] != plan.queries[:index]
                    ):
                        raise AppError(
                            "Repair changed the source plan. Start a new question.", code="plan_invalid"
                        )
                    query = repaired.queries[index]
                    plan = repaired
        diagnostics = None
        if plan.fusion:
            await self.repo.emit(
                "progress",
                {"stage": "relationship", "message": "Checking join keys, coverage, and cardinality"},
            )
            async with self.fusion_slots:
                fused = await fuse(
                    results[0],
                    results[1],
                    plan.fusion,
                    self.settings.fusion_timeout_seconds,
                    self.settings.fusion_row_limit,
                )
            rows, columns, diagnostics = fused["rows"], fused["columns"], fused["diagnostics"]
            assumptions = plan.assumptions + [
                plan.fusion.relationship,
                "This cross-source relationship was inferred automatically.",
                diagnostics["snapshot"],
            ]
        else:
            rows, columns, assumptions = results[0].rows, results[0].columns, list(plan.assumptions)
        complete = all(result.complete for result in results)
        if not complete:
            assumptions.append(
                "Source result exceeded the row cap. This is a bounded partial result, not a complete total."
            )
        names = {column["name"] for column in columns}
        visualization = plan.visualization
        if visualization.x and visualization.x not in names or any(y not in names for y in visualization.y):
            visualization = VisualizationSpec(type="table", title=plan.title)
        visualization = normalized_spec(visualization, columns, json_rows(rows))
        artifact_id = uuid.uuid4().hex
        artifact = ResultArtifact(
            id=artifact_id,
            conversation_id=conversation_id,
            title=plan.title,
            columns=columns,
            row_count=len(rows),
            preview_count=min(len(rows), self.settings.preview_rows),
            complete=complete,
            visualization=visualization,
            provenance=[result.model_dump(mode="json", exclude={"rows"}) for result in results],
            assumptions=assumptions,
            join_diagnostics=diagnostics,
            created_at=now_iso(),
        )
        encoded_rows = json_rows(rows)
        page, page_index, page_size = [], 0, 0
        for row in encoded_rows:
            size = len(json.dumps(row).encode())
            if size > 180_000:
                raise AppError(
                    "A result row exceeds the storage budget. Select smaller columns.",
                    code="result_too_large",
                )
            if page and (page_size + size > 180_000 or len(page) >= 250):
                await self.repo.write(
                    f"artifacts/{artifact_id}/pages", str(page_index), {"index": page_index, "rows": page}
                )
                page, page_size, page_index = [], 0, page_index + 1
            page.append(row)
            page_size += size
        if page:
            await self.repo.write(
                f"artifacts/{artifact_id}/pages", str(page_index), {"index": page_index, "rows": page}
            )
        value = artifact.model_dump(mode="json") | {
            "question": question,
            "analysis_id": analysis_id,
            "run_id": lease["run_id"],
            "data_profile": self.settings.data_profile,
            "data_coverage": self.connectors.coverage,
            "ai": model_evidence(self.settings),
            "page_count": page_index + 1 if encoded_rows else 0,
            "retrieval": retrieval,
            "skills_used": skills_used,
            "skill_warnings": skill_warnings,
            "metric_snapshots": plan.metric_snapshots,
            "metric_scope": plan.metric_scope,
            "metric_resolution": "catalog" if plan.metric_snapshots else "ad_hoc",
        }
        from app.metrics import evidence_signature
        from app.timesfm import digest

        value["schema_hash"] = digest(
            [await self.ai.schema(s) for s in sorted({q.source for q in plan.queries})]
        )
        value["evidence_signature"] = evidence_signature(
            plan, self.settings.data_profile, value["schema_hash"], self.connectors.coverage
        )
        await self.repo.write("artifacts", artifact_id, value)
        message_id = await self.save_message(
            conversation_id,
            "assistant",
            f"The query returned {len(rows):,} rows. Preparing the explanation…",
            artifact_id,
            skills_used=skills_used,
            skill_warnings=skill_warnings,
        )
        # Rows live in bounded pages; replay events must fit a Firestore document.
        await self.repo.emit("artifact", value)
        await self.repo.emit(
            "progress", {"stage": "answer", "message": "Explaining the result and its assumptions"}
        )
        plan.assumptions = assumptions
        try:
            answer = await self.ai.answer(
                question, plan, rows, diagnostics, conversation_id, skills=skills, analysis_id=analysis_id
            )
        except (AppError, TimeoutError, APIError, ValidationError) as exc:
            logger.warning("Interpretation unavailable: %s", type(exc).__name__)
            answer = Answer(
                explanation=f"The query returned {len(rows):,} rows. The AI explanation is unavailable; inspect the result and SQL evidence."
            )
        if not complete:
            answer.explanation = "Partial result: the source row limit was reached. " + answer.explanation
        await self.save_message(
            conversation_id,
            "assistant",
            answer.explanation,
            artifact_id,
            answer.followups,
            message_id=message_id,
            skills_used=skills_used,
            skill_warnings=skill_warnings,
        )
        await self.repo.emit("answer", answer.model_dump())
        return {
            "explanation": answer.explanation,
            "artifact_id": artifact_id,
            "assumptions": assumptions,
            "join_diagnostics": diagnostics,
            "skills_used": skills_used,
            "skill_warnings": skill_warnings,
        }

    async def save_message(
        self,
        conversation_id,
        role,
        text,
        artifact_id=None,
        followups=None,
        message_id=None,
        *,
        skills_used=None,
        skill_warnings=None,
    ):
        lease = active_lease.get()
        key = message_id or uuid.uuid4().hex
        previous = (
            await self.repo.store.get(f"conversations/{conversation_id}/messages", key)
            if message_id
            else None
        )
        await self.repo.write(
            f"conversations/{conversation_id}/messages",
            key,
            {
                "id": key,
                "run_id": lease["run_id"],
                "role": role,
                "text": text,
                "artifact_id": artifact_id,
                "followups": followups or [],
                "created_at": previous["created_at"] if previous else now_iso(),
                "status": "complete",
                "skills_used": skills_used or [],
                "skill_warnings": skill_warnings or [],
            },
        )
        return key

    async def cancel(self, run_id: str, guest_id: str):
        run = await self.repo.run(run_id)
        if run["guest_id"] != guest_id:
            raise AppError("Only the guest who started this run can cancel it.", 403, "forbidden")
        key = ("runs", run_id)

        def mutate(docs):
            value = docs[key]
            value["cancel_requested"] = True
            return {key: value}, None

        await self.repo.store.atomic([key], mutate)
        if run_id in self.tasks:
            self.tasks[run_id].cancel()
        return await self.connectors.cancel(run_id)

    async def close(self):
        tasks = list(self.tasks.values())
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
