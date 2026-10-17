"""Bounded dashboard snapshots and downloads from saved evidence only."""

import asyncio
import hashlib
import io
import json
import multiprocessing as mp
import textwrap
import time
import zipfile
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

from app.chart_presentation import csv_line, metadata, number, present, saved_rows
from app.errors import AppError
from app.report_exports import format_axis, zip_entry

FORMATS = {
    "png": ("image/png", "png"),
    "jpeg": ("image/jpeg", "jpg"),
    "pdf": ("application/pdf", "pdf"),
    "data": ("application/zip", "zip"),
    "json": ("application/json", "json"),
}
MAX_BYTES = 32 * 1024 * 1024
MAX_ROWS = 200_000
MAX_PIXELS = 24_000_000


async def snapshot(service, board_id, expected_revision):
    board = await service.detail(board_id)
    if board["deleted"]:
        raise AppError("Restore this dashboard before downloading it.", 409, "dashboard_deleted")
    if board["revision"] != expected_revision:
        raise AppError("This dashboard changed. Reload it before downloading.", 409, "dashboard_conflict")
    datasets, total_bytes, total_rows = {}, 0, 0
    for item in board["items"]:
        key = item["artifact_id"]
        if key in datasets:
            continue
        artifact = await service.store.get("artifacts", key)
        if not artifact:
            raise AppError(
                "A saved card is unavailable. Restore its evidence before exporting.",
                409,
                "artifact_incomplete",
            )
        rows = []
        async for row in saved_rows(service.store, artifact):
            total_bytes += len(json.dumps(row).encode())
            total_rows += 1
            if total_bytes > MAX_BYTES or total_rows > MAX_ROWS:
                raise AppError(
                    "Dashboard download exceeds the saved-data budget. Download individual card CSVs instead.",
                    413,
                    "dashboard_export_large",
                )
            rows.append(row)
        datasets[key] = (artifact, rows)
    if (await service.get(board_id))["revision"] != expected_revision:
        raise AppError(
            "The dashboard changed while preparing the download. Reload and try again.",
            409,
            "dashboard_conflict",
        )
    return board, datasets


def prepare_card(item, artifact, rows):
    view = item["view"]
    if view["view"] in {"table", "kpi"}:
        spec = metadata(artifact["visualization"], artifact["columns"], rows)
        return {
            "rows": rows,
            "visualization": spec,
            "coverage": {
                "selected_rows": len(rows),
                "plotted_rows": min(20, len(rows)),
                "complete": artifact["complete"],
                "sampled": False,
                "omitted_categories": 0,
            },
            "scope": {"start": None, "end": None},
            "warning": None,
        }
    return present(
        artifact,
        rows,
        start=date.fromisoformat(view["start"]) if view.get("start") else None,
        end=date.fromisoformat(view["end"]) if view.get("end") else None,
        primary=view.get("primary"),
        order=view.get("order", "value_desc"),
        top=view.get("top", 10),
        view=view["view"],
    )


def card_notes(item, artifact, prepared):
    coverage, scope = prepared["coverage"], prepared["scope"]
    notes = [
        f"Artifact {artifact['id']} · {artifact['row_count']} full saved rows · {'Complete saved result' if artifact['complete'] else 'PARTIAL source result; not a population total'}"
    ]
    if item["view"]["view"] not in {"table", "kpi"}:
        notes.append(
            f"Scope: {scope.get('start') or 'start of saved result'} to {scope.get('end') or 'end of saved result'} · {coverage['plotted_rows']} plotted / {coverage['selected_rows']} in scope."
        )
    if coverage["sampled"]:
        notes.append("Extrema-preserving sample; summaries use the complete selected scope.")
    if coverage["omitted_categories"]:
        notes.append(f"{coverage['omitted_categories']} categories omitted; no Other grouping.")
    if item["view"]["view"] == "table":
        notes.append(
            f"Image/PDF table preview: up to 20 rows and 8 columns; CSV ZIP contains all {artifact['row_count']} saved rows and original columns. Long preview cells are shortened."
        )
    if prepared["visualization"].get("partial_periods"):
        notes.append("Incomplete periods excluded from period-change comparisons.")
    if prepared.get("warning"):
        notes.append(prepared["warning"])
    if artifact.get("prediction"):
        p = artifact["prediction"]
        notes.append(
            f"PREDICTION · Observed cutoff {p.get('cutoff', 'not recorded')} · Future values are estimates; scenarios are conditional, not causal effects."
        )
        band = p.get("interval")
        notes.append(
            f"Nominal {band['level'] * 100:g}% interval; observed backtest coverage {band['coverage'] * 100:.1f}%; future coverage is not guaranteed."
            if band
            else "Validated prediction intervals unavailable; uncertainty is not quantified."
        )
    notes.extend(f"{p['source']} queried {p['executed_at']}" for p in artifact.get("provenance", []))
    notes.extend(artifact.get("assumptions", []))
    if artifact.get("report_id"):
        notes.append(f"Report {artifact['report_id']} · immutable version {artifact.get('report_version')}")
    return notes


def plot_images(item, artifact, prepared):
    import matplotlib

    matplotlib.use("Agg")
    from matplotlib.figure import Figure
    from matplotlib.ticker import FuncFormatter
    from PIL import Image

    rows, spec, view = prepared["rows"], prepared["visualization"], item["view"]
    kind, x = view["view"], spec.get("x")
    if kind in {"table", "kpi"} or not rows or prepared.get("warning"):
        return []
    measures = [m for m in spec["measures"] if m["field"] in view["visible_measures"]]
    if kind == "scatter":
        by_field = {m["field"]: m for m in spec["measures"]}
        for field in (view["scatter_x"], view["scatter_y"]):
            by_field.setdefault(field, {"field": field, "label": field, "unit": "number"})
        groups = [[by_field[view["scatter_x"]], by_field[view["scatter_y"]]]]
    elif kind == "pie":
        if not prepared["composition"]:
            raise ValueError("The saved pie is not a valid composition.")
        groups = [[next(m for m in measures if m["field"] == prepared["primary"])]]
    else:
        units = {}
        for measure in measures:
            units.setdefault(
                (measure["unit"], measure.get("currency"), measure.get("percent_scale")), []
            ).append(measure)
        groups = list(units.values())
    palette = ["#2563eb", "#7c3aed", "#0f766e", "#b45309", "#be185d"]
    colors = {m["field"]: palette[i % len(palette)] for i, m in enumerate(spec["measures"])}
    images = []
    for group in groups:
        figure = Figure(
            figsize=(9, max(4.1, len(rows) * 0.55 + 1) if kind == "bar" else 4.1), layout="constrained"
        )
        axes = figure.subplots()
        if kind == "scatter":
            a, b = group
            axes.scatter(
                [r.get(a["field"]) for r in rows], [r.get(b["field"]) for r in rows], s=20, color=palette[0]
            )
            axes.set_xlabel(a.get("label") or a["field"])
            axes.xaxis.set_major_formatter(FuncFormatter(lambda value, _: format_axis(value, a)))
        elif kind == "pie":
            axes.pie(
                [r[group[0]["field"]] for r in rows],
                labels=[textwrap.fill(str(r[x]), 22) for r in rows],
                colors=palette,
                autopct="%1.1f%%",
            )
        else:
            positions = list(range(len(rows)))
            for index, measure in enumerate(group):
                values = [
                    float(r[measure["field"]]) if r.get(measure["field"]) is not None else float("nan")
                    for r in rows
                ]
                label = measure.get("label") or measure["field"]
                color = colors[measure["field"]]
                comparator = measure.get("role") in {"target", "comparison", "forecast", "scenario"}
                if kind == "bar":
                    offsets = [p + (index - (len(group) - 1) / 2) * 0.8 / len(group) for p in positions]
                    axes.barh(
                        offsets,
                        values,
                        height=0.8 / len(group),
                        label=label,
                        color=color,
                        alpha=0.65 if comparator else 0.9,
                    )
                else:
                    axes.plot(
                        positions,
                        values,
                        label=label,
                        color=color,
                        linewidth=2,
                        linestyle="--" if comparator else "-",
                    )
                    if kind == "area":
                        axes.fill_between(positions, values, alpha=0.10, color=color)
                    if view.get("highlights") and not comparator:
                        valid = [(i, v) for i, v in enumerate(values) if v == v]
                        if valid:
                            marks = {valid[-1], max(valid, key=lambda pair: pair[1])}
                            axes.scatter(
                                [i for i, _ in marks], [v for _, v in marks], color=color, s=25, zorder=5
                            )
            if kind == "bar":
                axes.set_yticks(positions, [textwrap.fill(str(r[x]), 24) for r in rows], fontsize=8)
                axes.invert_yaxis()
                axes.axvline(0, color="#64748b", linewidth=0.6)
                axes.xaxis.set_major_formatter(FuncFormatter(lambda value, _: format_axis(value, group[0])))
            else:
                ticks = list(range(0, len(rows), max(1, len(rows) // 5)))
                axes.set_xticks(
                    ticks,
                    [str(rows[i].get(x) or "Missing") for i in ticks],
                    rotation=20,
                    ha="right",
                    fontsize=8,
                )
                if (artifact.get("prediction") or {}).get("interval") and any(
                    m.get("role") == "forecast" for m in group
                ):
                    axes.fill_between(
                        positions,
                        [
                            r.get("interval_lower") if r.get("interval_lower") is not None else float("nan")
                            for r in rows
                        ],
                        [
                            r.get("interval_upper") if r.get("interval_upper") is not None else float("nan")
                            for r in rows
                        ],
                        alpha=0.12,
                        color=palette[1],
                        label="Prediction interval",
                    )
            axes.legend(fontsize=8, loc="best")
        if kind not in {"pie", "bar"}:
            axes.yaxis.set_major_formatter(
                FuncFormatter(
                    lambda value, _: format_axis(value, group[-1] if kind == "scatter" else group[0])
                )
            )
        axes.set_title(
            textwrap.fill(
                " / ".join(
                    (m.get("label") or m["field"])
                    + (f" ({m.get('currency') or m['unit']})" if m.get("unit") != "number" else "")
                    for m in group
                ),
                78,
            ),
            fontsize=10,
            loc="left",
        )
        if kind != "pie":
            axes.grid(alpha=0.12)
        buffer = io.BytesIO()
        figure.savefig(buffer, format="png", dpi=100)
        figure.clear()
        images.append(Image.open(io.BytesIO(buffer.getvalue())).convert("RGB"))
    return images


def text_image(lines, width=900, size=15, title=False):
    import matplotlib
    from PIL import Image, ImageDraw, ImageFont

    font = ImageFont.truetype(str(Path(matplotlib.get_data_path()) / "fonts/ttf/DejaVuSans.ttf"), size)
    wrapped = [
        line
        for value in lines
        for line in textwrap.wrap(
            str(value), max(20, int((width - 48) / (size * 0.57))), break_long_words=True
        )
    ]
    image = Image.new(
        "RGB", (width, max(32, len(wrapped) * (size + 8) + 24)), "#eff6ff" if title else "white"
    )
    draw = ImageDraw.Draw(image)
    for i, line in enumerate(wrapped):
        draw.text((24, 12 + i * (size + 8)), line, font=font, fill="#0f172a")
    return image


def display_value(value, measure, decimals):
    parsed = number(value)
    if parsed is None:
        return "Not available"
    unit = measure.get("unit", "number")
    if unit == "percent" and measure.get("percent_scale") == "fraction":
        parsed *= 100
    digits = 0 if unit == "count" else decimals
    return (
        (f"{measure['currency']} " if unit == "currency" and measure.get("currency") else "")
        + f"{parsed:,.{digits}f}"
        + ("%" if unit == "percent" else "")
    )


def card_image(item, artifact, rows):
    from PIL import Image

    prepared = prepare_card(item, artifact, rows)
    notes = card_notes(item, artifact, prepared)
    pieces = [text_image([item["title"]], size=22, title=True)]
    if item.get("note"):
        pieces.append(text_image([item["note"]]))
    pieces.extend(plot_images(item, artifact, prepared))
    if item["view"]["view"] in {"table", "kpi"}:
        names = [c["name"] for c in artifact["columns"]]
        if item["view"]["view"] == "kpi":
            measures = {m["field"]: m for m in prepared["visualization"]["measures"]}
            pieces.append(
                text_image(
                    [
                        f"{measures.get(n, {}).get('label') or n}: {display_value(rows[0].get(n) if rows else None, measures.get(n, {}), item['view']['decimals'])}"
                        for n in item["view"]["visible_measures"]
                    ],
                    size=24,
                )
            )
        else:
            pieces.append(
                text_image(
                    [" | ".join(names[:8])]
                    + [
                        " | ".join(
                            str(r.get(n))[:80] if r.get(n) is not None else "Not available" for n in names[:8]
                        )
                        for r in rows[:20]
                    ],
                    size=14,
                )
            )
    pieces.append(text_image(notes, size=13))
    height = sum(p.height for p in pieces)
    if height * 900 > MAX_PIXELS:
        raise ValueError("Card is too large to export.")
    image = Image.new("RGB", (900, height), "white")
    y = 0
    for piece in pieces:
        image.paste(piece, (0, y))
        y += piece.height
    return image, notes


def manifest(board, datasets):
    return {
        "format_version": 1,
        "dashboard": board,
        "scope": "Published saved card views; CSV files contain full saved results, independent of visual filters.",
        "notes": "Public dashboard. Saved source timestamps are independent; this is not a synchronized source snapshot. No SQL or model calls.",
        "datasets": [
            {
                "artifact_id": key,
                "columns": artifact["columns"],
                "row_count": len(rows),
                "complete": artifact["complete"],
                "provenance": artifact["provenance"],
                "assumptions": artifact.get("assumptions", []),
                "prediction": artifact.get("prediction"),
                "join_diagnostics": artifact.get("join_diagnostics"),
                "skills_used": artifact.get("skills_used", []),
                "report_id": artifact.get("report_id"),
                "report_version": artifact.get("report_version"),
            }
            for key, (artifact, rows) in datasets.items()
        ],
    }


def render_file(board, datasets, kind):
    info = manifest(board, datasets)
    if kind == "json":
        return json.dumps(info, indent=2, ensure_ascii=False).encode()
    if kind == "data":
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            for record in info["datasets"]:
                artifact, rows = datasets[record["artifact_id"]]
                columns = [c["name"] for c in artifact["columns"]]
                value = (
                    "\ufeff"
                    + csv_line(columns)
                    + "".join(csv_line([r.get(c) for c in columns]) for r in rows)
                ).encode()
                filename = record["artifact_id"] + ".csv"
                zip_entry(archive, filename, value)
                record.update(file=filename, sha256=hashlib.sha256(value).hexdigest())
            zip_entry(archive, "manifest.json", json.dumps(info, indent=2))
        return buffer.getvalue()
    if kind == "pdf":
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

        buffer = io.BytesIO()
        styles = getSampleStyleSheet()
        story = [
            Paragraph(escape(board["name"]), styles["Title"]),
            Paragraph(
                escape(f"Public dashboard · {board['id']} · Revision {board['revision']}"), styles["Normal"]
            ),
            Paragraph(escape(board["description"] or "Saved analytical results"), styles["Normal"]),
            Paragraph(escape(info["notes"]), styles["Normal"]),
            Spacer(1, 16),
        ]
        for item in board["items"]:
            artifact, rows = datasets[item["artifact_id"]]
            prepared = prepare_card(item, artifact, rows)
            notes = card_notes(item, artifact, prepared)
            story.append(Paragraph(escape(item["title"]), styles["Heading2"]))
            if item.get("note"):
                story.append(Paragraph(escape(item["note"]), styles["Normal"]))
            for image in plot_images(item, artifact, prepared):
                blob = io.BytesIO()
                image.save(blob, format="PNG")
                width = min(490, 620 * image.width / image.height)
                story.append(
                    Image(io.BytesIO(blob.getvalue()), width=width, height=width * image.height / image.width)
                )
            if item["view"]["view"] == "kpi":
                measures = {m["field"]: m for m in prepared["visualization"]["measures"]}
                for field in item["view"]["visible_measures"]:
                    value = display_value(
                        rows[0].get(field) if rows else None,
                        measures.get(field, {}),
                        item["view"]["decimals"],
                    )
                    story.append(
                        Paragraph(
                            escape(f"{measures.get(field, {}).get('label') or field}: {value}"),
                            styles["Heading2"],
                        )
                    )
            elif item["view"]["view"] == "table":
                names = [c["name"] for c in artifact["columns"]][:8]
                cells = [names] + [
                    [str(r.get(n))[:80] if r.get(n) is not None else "Not available" for n in names]
                    for r in rows[:20]
                ]
                if names:
                    table = Table(
                        [[Paragraph(escape(str(cell)), styles["Normal"]) for cell in row] for row in cells],
                        colWidths=[490 / len(names)] * len(names),
                        repeatRows=1,
                        hAlign="LEFT",
                    )
                    table.setStyle(
                        TableStyle(
                            [
                                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                ("GRID", (0, 0), (-1, -1), 0.25, "#cbd5e1"),
                                ("BACKGROUND", (0, 0), (-1, 0), "#eff6ff"),
                            ]
                        )
                    )
                    story.append(table)
            for note in notes:
                story.append(Paragraph(escape(note), styles["Normal"]))
            story.append(Spacer(1, 18))

        def footer(canvas, doc):
            canvas.setFont("Helvetica", 8)
            canvas.drawString(36, 24, f"Querylane · Dashboard revision {board['revision']} · Page {doc.page}")

        SimpleDocTemplate(
            buffer,
            title=board["name"],
            author="Querylane",
            subject=f"Dashboard {board['id']} revision {board['revision']}",
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=36,
        ).build(story, onFirstPage=footer, onLaterPages=footer)
        return buffer.getvalue()
    from PIL import Image

    cards = [(item, *card_image(item, *datasets[item["artifact_id"]])) for item in board["items"]]
    header = text_image(
        [
            board["name"],
            board["description"],
            f"Public dashboard · Revision {board['revision']} · {board['card_count']} saved cards",
            info["notes"],
        ],
        width=1800,
        size=22,
        title=True,
    )
    placements, y, row_height, column = [], header.height + 16, 0, 0
    for item, image, _ in cards:
        wide = item["width"] == "wide"
        if wide:
            image = image.resize((1800, image.height * 2))
        if wide and column:
            y += row_height + 16
            column, row_height = 0, 0
        placements.append((image, 0 if wide else column * 900, y))
        row_height = max(row_height, image.height)
        if wide or column:
            y += row_height + 16
            column, row_height = 0, 0
        else:
            column = 1
    height = y + row_height + 16
    if height * 1800 > MAX_PIXELS:
        raise ValueError("Dashboard image is too large. Choose PDF or CSV ZIP instead.")
    image = Image.new("RGB", (1800, height), "#e2e8f0")
    image.paste(header, (0, 0))
    for card, left, top in placements:
        image.paste(card, (left, top))
    buffer = io.BytesIO()
    image.save(
        buffer, format="JPEG" if kind == "jpeg" else "PNG", **({"quality": 94} if kind == "jpeg" else {})
    )
    return buffer.getvalue()


def render_entry(pipe, board, datasets, kind):
    try:
        pipe.send({"data": render_file(board, datasets, kind)})
    except Exception as error:
        pipe.send({"error": str(error)[:300]})
    finally:
        pipe.close()


async def download(service, board_id, expected_revision, kind):
    if service.export_slot.locked():
        raise AppError(
            "A dashboard download is being prepared. Try again shortly.", 429, "dashboard_export_busy"
        )
    async with service.export_slot:
        try:
            async with asyncio.timeout(60):
                board, datasets = await snapshot(service, board_id, expected_revision)
        except TimeoutError as exc:
            raise AppError(
                "Saved evidence took too long to load. Retry or download individual card CSVs.",
                503,
                "dashboard_export_timeout",
            ) from exc
        context = mp.get_context("spawn")
        parent, child = context.Pipe(duplex=False)
        process = context.Process(target=render_entry, args=(child, board, datasets, kind), daemon=True)
        process.start()
        child.close()
        started = time.monotonic()
        try:
            while not parent.poll():
                if time.monotonic() - started > 45 or not process.is_alive():
                    raise AppError(
                        "Dashboard rendering timed out. Try a data download or fewer cards.",
                        503,
                        "dashboard_export_timeout",
                    )
                await asyncio.sleep(0.05)
            value = parent.recv()
            if "error" in value:
                raise AppError(
                    "Could not render the dashboard. Try CSV ZIP or JSON, or export fewer cards.",
                    422,
                    "dashboard_export_failed",
                )
            return value["data"]
        finally:
            if process.is_alive():
                process.terminate()
            await asyncio.to_thread(process.join, 2)
            if process.is_alive():
                process.kill()
                await asyncio.to_thread(process.join, 2)
            parent.close()
