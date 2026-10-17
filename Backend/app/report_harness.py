"""ADK graph orchestration with global policy and explicit application checkpoints."""

from contextlib import aclosing
from contextvars import ContextVar

from google.adk import Workflow
from google.adk.agents.run_config import RunConfig
from google.adk.apps import App
from google.adk.plugins.base_plugin import BasePlugin
from google.adk.runners import Runner
from google.genai import types

from app.errors import AppError

active_report_policy = ContextVar("active_report_policy", default=None)


class ReportPolicy(BasePlugin):
    def __init__(self, repository, lease, sessions=None):
        super().__init__(name="report_policy")
        self.repository, self.lease, self.sessions = repository, lease, sessions
        self.reservations = {}

    async def before_model_callback(self, *, callback_context, llm_request):
        if llm_request.tools_dict:
            raise AppError("Report models cannot invoke unrestricted tools.", 403, "report_tool_denied")
        budget = llm_request.config.max_output_tokens or 1536
        await self.repository.spend(self.lease, model_calls=1, output_tokens=budget)
        self.reservations[callback_context.invocation_id] = budget
        return None

    async def after_model_callback(self, *, callback_context, llm_response):
        usage = llm_response.usage_metadata
        reserved = self.reservations.pop(callback_context.invocation_id, None)
        if reserved and usage:
            actual = (usage.candidates_token_count or 0) + (usage.thoughts_token_count or 0)
            await self.repository.spend(self.lease, output_tokens=actual - reserved)
        return None

    async def before_tool_callback(self, *, tool, tool_args, tool_context):
        raise AppError("Model-selected report tools are not allowed.", 403, "report_tool_denied")


async def run_report_graph(engine, run, lease):
    """Graph nodes carry only a run identifier. Bodies live in fenced checkpoints."""
    failure = []

    async def invoke(stage):
        if failure:
            return
        try:
            await stage(run, lease)
        except Exception as exc:
            # ADK wraps node exceptions; retain clarification and policy failures.
            failure.append(exc)

    async def prepare(node_input: str) -> str:
        await invoke(engine.prepare)
        return run["id"]

    async def gather_evidence(node_input: str) -> str:
        await invoke(engine.gather)
        return node_input

    async def analyze(node_input: str) -> str:
        await invoke(engine.analyze)
        return node_input

    async def compose_and_review(node_input: str) -> str:
        await invoke(engine.compose)
        return node_input

    async def render_and_publish(node_input: str) -> str:
        await invoke(engine.publish)
        return node_input

    workflow = Workflow(
        name="advanced_report",
        max_concurrency=2,
        edges=[("START", prepare, gather_evidence, analyze, compose_and_review, render_and_publish)],
    )
    sessions = getattr(engine.services, "report_sessions", engine.services.sessions)
    policy = ReportPolicy(engine.repo, lease, sessions)
    app = App(name="querylane_reports", root_agent=workflow, plugins=[policy])
    # Fresh ADK scope on every delivery. Saved application stages skip completed work;
    # no truncated event history or experimental invocation resumption is required.
    session_id = f"report_{run['id']}_{lease['generation']}"
    await sessions.create_session(app_name=app.name, user_id="public-demo", session_id=session_id)
    runner = Runner(app=app, session_service=sessions)
    token = active_report_policy.set(policy)
    try:
        async with aclosing(
            runner.run_async(
                user_id="public-demo",
                session_id=session_id,
                new_message=types.Content(role="user", parts=[types.Part(text=run["id"])]),
                run_config=RunConfig(max_llm_calls=engine.settings.report_model_calls),
            )
        ) as events:
            async for event in events:
                if event.error_code:
                    raise AppError(
                        "The report graph could not finish. Retry with a narrower question.",
                        502,
                        "report_graph_error",
                    )
        if failure:
            raise failure[0]
    finally:
        active_report_policy.reset(token)
