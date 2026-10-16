/** Native SVG/canvas export. All text is drawn locally; no external image or font requests. */
export function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export async function exportChartPng(
  container: HTMLElement,
  title: string,
  subtitle: string,
  notes: string,
  legends: { label: string; color: string; dashed?: boolean }[],
) {
  const svgs = Array.from(
    container.querySelectorAll<SVGSVGElement>("svg.recharts-surface"),
  );
  if (!svgs.length)
    throw new Error("A chart must finish loading before it can be exported.");
  const canvas = document.createElement("canvas");
  const width = Math.max(960, Math.min(1600, container.clientWidth));
  const ctx = canvas.getContext("2d");
  if (!ctx) throw new Error("Image export is unavailable in this browser.");
  const styles = getComputedStyle(container);
  const background =
    getComputedStyle(document.body).backgroundColor || "#ffffff";
  const foreground = styles.color;
  canvas.width = width * 2;
  const heights = svgs.map((svg) =>
    Math.max(
      220,
      Math.min(
        600,
        (width * svg.getBoundingClientRect().height) /
          Math.max(1, svg.getBoundingClientRect().width),
      ),
    ),
  );
  ctx.font = "14px sans-serif";
  function wrap(text: string) {
    const lines: string[] = [];
    let line = "";
    for (const word of text.split(/\s+/)) {
      const candidate = line ? `${line} ${word}` : word;
      if (ctx!.measureText(candidate).width > width - 64 && line) {
        lines.push(line);
        line = word;
      } else line = candidate;
    }
    if (line) lines.push(line);
    return lines;
  }
  ctx.font = "16px sans-serif";
  const headerLines = [...wrap(title), ...wrap(subtitle)];
  ctx.font = "14px sans-serif";
  const legendLines = legends.flatMap((legend) =>
    wrap(legend.label).map((label, index) => ({
      ...legend,
      label,
      swatch: index === 0,
    })),
  );
  const footerLines = wrap(notes);
  const headerHeight = 30 + headerLines.length * 24 + legendLines.length * 22;
  canvas.height =
    (headerHeight +
      heights.reduce((a, b) => a + b, 0) +
      footerLines.length * 22 +
      45) *
    2;
  ctx.scale(2, 2);
  ctx.fillStyle = background;
  ctx.fillRect(0, 0, canvas.width / 2, canvas.height / 2);
  ctx.fillStyle = foreground;
  ctx.font = "16px sans-serif";
  headerLines.forEach((line, i) => ctx.fillText(line, 24, 30 + i * 24));
  ctx.font = "14px sans-serif";
  legendLines.forEach((legend, index) => {
    const y = 30 + headerLines.length * 24 + index * 22;
    if (legend.swatch) {
      const resolver = document.createElement("span");
      resolver.style.color = legend.color;
      container.appendChild(resolver);
      ctx.strokeStyle = getComputedStyle(resolver).color;
      resolver.remove();
      ctx.lineWidth = 3;
      ctx.setLineDash(legend.dashed ? [5, 3] : []);
      ctx.beginPath();
      ctx.moveTo(24, y - 4);
      ctx.lineTo(42, y - 4);
      ctx.stroke();
      ctx.setLineDash([]);
    }
    ctx.fillStyle = foreground;
    ctx.fillText(legend.label, 52, y);
  });
  let y = headerHeight;
  for (let index = 0; index < svgs.length; index++) {
    const source = svgs[index];
    const clone = source.cloneNode(true) as SVGSVGElement;
    const originals = [
      source,
      ...Array.from(source.querySelectorAll<SVGElement>("*")),
    ];
    const copies = [
      clone,
      ...Array.from(clone.querySelectorAll<SVGElement>("*")),
    ];
    originals.forEach((node, i) => {
      const computed = getComputedStyle(node);
      for (const property of [
        "fill",
        "stroke",
        "stroke-width",
        "opacity",
        "fill-opacity",
        "stroke-opacity",
        "font-size",
        "font-weight",
        "stroke-dasharray",
        "visibility",
        "display",
      ])
        copies[i].style.setProperty(
          property,
          computed.getPropertyValue(property),
        );
      copies[i].style.fontFamily = "sans-serif";
    });
    clone.setAttribute("xmlns", "http://www.w3.org/2000/svg");
    clone
      .querySelectorAll("foreignObject, script, image")
      .forEach((node) => node.remove());
    const url = URL.createObjectURL(
      new Blob([new XMLSerializer().serializeToString(clone)], {
        type: "image/svg+xml;charset=utf-8",
      }),
    );
    try {
      const image = new Image();
      await new Promise<void>((resolve, reject) => {
        image.onload = () => resolve();
        image.onerror = () =>
          reject(new Error("Chart image could not be rendered."));
        image.src = url;
      });
      ctx.drawImage(image, 24, y, width - 48, heights[index]);
      y += heights[index];
    } finally {
      URL.revokeObjectURL(url);
    }
  }
  ctx.fillStyle = foreground;
  ctx.font = "14px sans-serif";
  footerLines.forEach((line, i) => ctx.fillText(line, 24, y + 24 + i * 22));
  const blob = await new Promise<Blob>((resolve, reject) =>
    canvas.toBlob(
      (value) =>
        value ? resolve(value) : reject(new Error("Chart export failed.")),
      "image/png",
    ),
  );
  downloadBlob(blob, "querylane-chart.png");
}
