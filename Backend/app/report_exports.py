"""Immutable report files. Rendering accepts saved evidence, never SQL or model tools."""

import asyncio
import hashlib
import io
import json
import multiprocessing as mp
import os
import re
import tempfile
import textwrap
import time
import zipfile
from functools import partial
from pathlib import Path
from xml.sax.saxutils import escape

from app.chart_presentation import csv_line, present
from app.errors import AppError

FORMATS = {
    "pdf": ("application/pdf", "pdf"),
    "docx": ("application/vnd.openxmlformats-officedocument.wordprocessingml.document", "docx"),
    "data": ("application/zip", "zip"),
}


def zip_entry(archive, name, data):
    entry = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
    entry.compress_type = zipfile.ZIP_DEFLATED
    archive.writestr(entry, data)


def format_axis(value, measure):
    unit = measure.get("unit", "number")
    if unit == "currency":
        return f"{measure.get('currency') or 'Currency'} {value:,.0f}"
    if unit == "percent":
        scaled = value * 100 if measure.get("percent_scale") == "fraction" else value
        return f"{scaled:,.1f}%"
    return f"{value:,.0f}" if unit == "count" else f"{value:,.2f}"


def chart_image(artifact, rows):
    os.environ.setdefault("MPLCONFIGDIR", "/tmp/querylane-matplotlib")
    import matplotlib

    matplotlib.use("Agg")
    from matplotlib.figure import Figure
    from matplotlib.ticker import FuncFormatter

    spec = artifact["visualization"]
    if spec["type"] in {"table", "kpi"} or not rows:
        return None
    view = spec["type"]
    presentation = present(artifact, rows, view=view)
    if view == "pie" and not presentation["composition"]["valid"]:
        return None
    if view == "scatter" and len(spec.get("y", [])) < 2:
        return None
    data = presentation["rows"]
    if not data:
        return None
    xs, ys = spec.get("x"), spec.get("y", [])
    if not xs or not ys:
        return None
    figure = Figure(figsize=(9, 4.4), layout="constrained")
    axes = figure.subplots()
    colors = ["#2563eb", "#7c3aed", "#0f766e", "#b45309"]
    for index, field in enumerate(ys):
        values = [float(row[field]) if row.get(field) is not None else float("nan") for row in data]
        label = next((m.get("label") for m in spec.get("measures", []) if m["field"] == field), None) or field
        if view == "bar":
            axes.bar([str(r[xs]) for r in data], values, alpha=0.75, label=label, color=colors[index % 4])
        elif view == "scatter" and len(ys) >= 2:
            axes.scatter([r[ys[0]] for r in data], [r[ys[1]] for r in data], s=16)
            break
        elif view == "pie":
            axes.pie(values, labels=[str(r[xs]) for r in data])
            break
        else:
            axes.plot(
                [str(r[xs]) for r in data],
                values,
                label=label,
                linewidth=1.8,
                linestyle="--" if field in {"forecast", "scenario"} else "-",
                color=colors[index % 4],
            )
    if view not in {"pie", "scatter"}:
        ticks = list(range(0, len(data), max(1, len(data) // 6)))
        axes.set_xticks(ticks, [str(data[i][xs]) for i in ticks], rotation=25, ha="right")
    measures = spec.get("measures", [])
    if measures and view != "pie":
        y_measure = measures[1] if view == "scatter" and len(measures) > 1 else measures[0]
        axes.yaxis.set_major_formatter(FuncFormatter(lambda value, _: format_axis(value, y_measure)))
        axes.set_ylabel(y_measure.get("label") or y_measure["field"])
        if view == "scatter" and len(measures) > 1:
            axes.xaxis.set_major_formatter(FuncFormatter(lambda value, _: format_axis(value, measures[0])))
            axes.set_xlabel(measures[0].get("label") or measures[0]["field"])
        else:
            axes.set_xlabel(xs)
    if artifact.get("prediction", {}).get("interval"):
        lo = [
            float(r.get("interval_lower")) if r.get("interval_lower") is not None else float("nan")
            for r in data
        ]
        hi = [
            float(r.get("interval_upper")) if r.get("interval_upper") is not None else float("nan")
            for r in data
        ]
        axes.fill_between(range(len(data)), lo, hi, color=colors[1], alpha=0.12, label="Prediction interval")
    # Artifact titles also appear as document headings. Wrap the chart copy so
    # long model-generated titles cannot extend beyond the image boundary.
    axes.set_title(textwrap.fill(artifact["title"], width=68), loc="left", fontsize=11)
    if view != "pie":
        axes.legend(loc="best", fontsize=8)
        axes.grid(axis="y", alpha=0.15)
    buffer = io.BytesIO()
    figure.savefig(buffer, format="png", dpi=150, metadata={"Software": "Querylane"})
    figure.clear()
    return buffer.getvalue()


def chart_images(artifact, rows):
    measures = artifact["visualization"].get("measures", [])
    if artifact["visualization"]["type"] in {"scatter", "pie", "table", "kpi"}:
        image = chart_image(artifact, rows)
        return [image] if image else []
    groups = {}
    for measure in measures:
        key = (measure["unit"], measure.get("currency"), measure.get("percent_scale"))
        groups.setdefault(key, []).append(measure)
    if len(groups) <= 1:
        image = chart_image(artifact, rows)
        return [image] if image else []
    images = []
    for key, group in groups.items():
        selected = artifact | {
            "visualization": artifact["visualization"] | {"y": [m["field"] for m in group], "measures": group}
        }
        selected["title"] = artifact["title"] + " — " + " / ".join(str(k) for k in key if k)
        image = chart_image(selected, rows)
        if image:
            images.append(image)
    return images


def plain(markdown):
    return re.sub(r"(?:\*\*|__|`|^#{1,6}\s+)", "", markdown, flags=re.M)


def _render(document, artifacts):
    from docx import Document
    from docx.shared import Inches
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.pdfgen.canvas import Canvas
    from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    styles = getSampleStyleSheet()
    pdf_buffer = io.BytesIO()
    word = Document()
    word.sections[0].left_margin = word.sections[0].right_margin = Inches(0.75)
    story = []

    def paragraph(text, style="BodyText"):
        text = plain(text)
        for line in text.splitlines():
            if line.strip():
                story.append(Paragraph(escape(line), styles[style]))
                word.add_paragraph(line, style="Heading 2" if style == "Heading2" else "Normal")
        story.append(Spacer(1, 8))

    story.append(Paragraph(escape(document["title"]), styles["Title"]))
    word.add_heading(document["title"], 0)
    paragraph(f"Public report · Version {document['version']} · {document['created_at']}")
    paragraph(f"Report ID: {document['report_id']}")
    paragraph(document["summary"])
    for section in document["sections"]:
        paragraph(section["title"], "Heading2")
        paragraph(section["markdown"])
        for artifact_id in section.get("artifact_ids", []):
            artifact, rows = artifacts[artifact_id]
            paragraph(artifact["title"], "Heading2")
            paragraph(
                f"Saved result: {len(rows)} rows. {'Complete' if artifact['complete'] else 'PARTIAL — not a population total'}. Artifact {artifact_id}."
            )
            if artifact["visualization"]["type"] not in {"table", "kpi"} and rows:
                presentation = present(artifact, rows, view=artifact["visualization"]["type"])
                coverage = presentation["coverage"]
                paragraph(
                    f"Chart coverage: {coverage['plotted_rows']} plotted of {coverage['selected_rows']} saved observations in scope; {coverage['omitted_categories']} categories omitted. {'Extrema-preserving sampling was applied.' if coverage['sampled'] else 'No visual sampling.'}"
                )
            images = chart_images(artifact, rows)
            if not images and artifact["visualization"]["type"] not in {"table", "kpi"}:
                paragraph(
                    "This saved scope cannot be represented faithfully by the requested static chart. Inspect its table and full CSV instead."
                )
            for image in images:
                story.append(Image(io.BytesIO(image), width=6.8 * inch, height=3.32 * inch))
                word.add_picture(io.BytesIO(image), width=Inches(6.8))
            names = [c["name"] for c in artifact["columns"]][:8]
            table_rows = [names] + [
                [str(r[c])[:100] if r.get(c) is not None else "Not available" for c in names]
                for r in rows[:20]
            ]
            if names:
                table = Table(
                    [[Paragraph(escape(str(c)), styles["BodyText"]) for c in row] for row in table_rows],
                    repeatRows=1,
                    hAlign="LEFT",
                    colWidths=[6.8 * inch / len(names)] * len(names),
                )
                table.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef2ff")),
                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("GRID", (0, 0), (-1, -1), 0.3, colors.lightgrey),
                        ]
                    )
                )
                story.append(table)
                wt = word.add_table(rows=1, cols=len(names))
                for cell, value in zip(wt.rows[0].cells, names):
                    cell.text = value
                for row in table_rows[1:]:
                    for cell, value in zip(wt.add_row().cells, row):
                        cell.text = value
            if len(rows) > 20 or len(artifact["columns"]) > 8:
                paragraph(
                    "Document preview shows up to 20 rows and 8 columns. Download CSV for all saved rows and original columns."
                )
    paragraph("Evidence and methodology", "Heading2")
    paragraph(
        f"Data profile: {document['data_profile']}. Model: {document['model']}. {document['mode_note']}"
    )
    for limitation in document["limitations"]:
        paragraph(limitation)
    for artifact_id, (artifact, _) in artifacts.items():
        paragraph(f"Evidence {artifact_id}: {artifact['title']}", "Heading2")
        for source in artifact["provenance"]:
            paragraph(
                f"{source['source']} · {source['executed_at']} · {source.get('job_id') or 'read-only query'}"
            )
            paragraph(source["sql"])
        for assumption in artifact.get("assumptions", []):
            paragraph(assumption)
        if artifact.get("prediction"):
            paragraph(json.dumps(artifact["prediction"], ensure_ascii=True))
    for skill in document.get("skills_used", []):
        paragraph(f"Skill: {skill['name']} · revision {skill['revision']}")

    def footer(canvas, doc):
        canvas.setFont("Helvetica", 8)
        canvas.drawString(
            0.6 * inch, 0.4 * inch, f"Querylane · version {document['version']} · page {doc.page}"
        )

    pdf = SimpleDocTemplate(
        pdf_buffer,
        title=document["title"],
        author="Querylane",
        subject=f"Report {document['report_id']} version {document['version']}",
        leftMargin=0.6 * inch,
        rightMargin=0.6 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
    )
    pdf.build(story, onFirstPage=footer, onLaterPages=footer, canvasmaker=partial(Canvas, invariant=1))
    wb = io.BytesIO()
    word.save(wb)
    # DOCX is a ZIP: normalize entry timestamps for stable checksums on recovery.
    normalized = io.BytesIO()
    with (
        zipfile.ZipFile(io.BytesIO(wb.getvalue())) as source,
        zipfile.ZipFile(normalized, "w", zipfile.ZIP_DEFLATED) as target,
    ):
        for name in source.namelist():
            zip_entry(target, name, source.read(name))
    data = io.BytesIO()
    manifest = {
        "report_id": document["report_id"],
        "version": document["version"],
        "created_at": document["created_at"],
        "data_profile": document["data_profile"],
        "claims": document["claims"],
        "datasets": [],
    }
    with zipfile.ZipFile(data, "w", zipfile.ZIP_DEFLATED) as archive:
        for artifact_id, (artifact, rows) in artifacts.items():
            columns = [c["name"] for c in artifact["columns"]]
            csv = "\ufeff" + csv_line(columns) + "".join(csv_line([r.get(c) for c in columns]) for r in rows)
            filename = f"{artifact_id}.csv"
            zip_entry(archive, filename, csv)
            manifest["datasets"].append(
                {
                    "file": filename,
                    "rows": len(rows),
                    "sha256": hashlib.sha256(csv.encode()).hexdigest(),
                    "complete": artifact["complete"],
                    "provenance": artifact["provenance"],
                    "prediction": artifact.get("prediction"),
                }
            )
        zip_entry(archive, "manifest.json", json.dumps(manifest, indent=2))
    return {"pdf": pdf_buffer.getvalue(), "docx": normalized.getvalue(), "data": data.getvalue()}


def _render_entry(pipe, document, artifacts):
    try:
        pipe.send({"files": _render(document, artifacts)})
    except Exception:
        pipe.send({"error": "Document rendering failed. Saved evidence is preserved for recovery."})
    finally:
        pipe.close()


async def render(document, artifacts, timeout=60):
    context = mp.get_context("spawn")
    parent, child = context.Pipe(duplex=False)
    process = context.Process(target=_render_entry, args=(child, document, artifacts), daemon=True)
    process.start()
    child.close()
    started = time.monotonic()
    try:
        while not parent.poll():
            if time.monotonic() - started >= timeout or not process.is_alive():
                raise AppError(
                    "Report export deadline reached. Evidence is preserved.", 503, "report_render_error"
                )
            await asyncio.sleep(0.05)
        value = parent.recv()
        if "error" in value:
            raise AppError(value["error"], 503, "report_render_error")
        return value["files"]
    finally:
        if process.is_alive():
            process.terminate()
        await asyncio.to_thread(process.join, 2)
        if process.is_alive():
            process.kill()
            await asyncio.to_thread(process.join, 2)
        parent.close()


class ExportStorage:
    def __init__(self, settings, credentials=None):
        self.settings, self.credentials = settings, credentials
        self.client = None
        if settings.report_bucket:
            from google.cloud import storage

            self.client = storage.Client(project=settings.google_cloud_project, credentials=credentials)

    def _path(self, key):
        root = Path(self.settings.report_local_directory).resolve()
        path = (root / key).resolve()
        if not path.is_relative_to(root):
            raise AppError("Invalid export path.", 422)
        return path

    async def save(self, key, content, content_type):
        sha = hashlib.sha256(content).hexdigest()

        def write():
            if self.client:
                from google.api_core.exceptions import PreconditionFailed

                blob = self.client.bucket(self.settings.report_bucket).blob(key)
                blob.metadata = {"sha256": sha}
                try:
                    blob.upload_from_string(
                        content, content_type=content_type, if_generation_match=0, timeout=30
                    )
                except PreconditionFailed:
                    blob.reload(timeout=15)
                    if blob.metadata.get("sha256") != sha:
                        raise AppError(
                            "An immutable export already exists with different content.",
                            409,
                            "report_immutable",
                        )
            else:
                path = self._path(key)
                path.parent.mkdir(parents=True, exist_ok=True)
                handle, temporary = tempfile.mkstemp(prefix=".report-", dir=path.parent)
                try:
                    with os.fdopen(handle, "wb") as file:
                        file.write(content)
                        file.flush()
                        os.fsync(file.fileno())
                    try:
                        os.link(temporary, path)
                    except FileExistsError:
                        if hashlib.sha256(path.read_bytes()).hexdigest() != sha:
                            raise AppError("Immutable export conflict.", 409, "report_immutable")
                finally:
                    Path(temporary).unlink(missing_ok=True)

        await asyncio.to_thread(write)
        return {"key": key, "sha256": sha, "size": len(content), "content_type": content_type}

    async def read(self, metadata):
        def read():
            return (
                self.client.bucket(self.settings.report_bucket)
                .blob(metadata["key"])
                .download_as_bytes(timeout=30)
                if self.client
                else self._path(metadata["key"]).read_bytes()
            )

        try:
            value = await asyncio.to_thread(read)
        except Exception as exc:
            raise AppError(
                "This export is unavailable. Contact the operator; no queries were rerun.",
                503,
                "report_export_unavailable",
            ) from exc
        if hashlib.sha256(value).hexdigest() != metadata["sha256"]:
            raise AppError("Export integrity check failed.", 503, "report_export_integrity")
        return value

    async def delete(self, metadata):
        def remove():
            if self.client:
                from google.api_core.exceptions import NotFound

                try:
                    self.client.bucket(self.settings.report_bucket).blob(metadata["key"]).delete(timeout=30)
                except NotFound:
                    pass
            else:
                self._path(metadata["key"]).unlink(missing_ok=True)

        await asyncio.to_thread(remove)

    async def close(self):
        if self.client:
            await asyncio.to_thread(self.client.close)
