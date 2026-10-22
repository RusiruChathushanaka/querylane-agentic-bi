/** Local browser diagnostics only; no telemetry, question text or credentials. */
export function loadingMark(name: string) {
  if (typeof performance !== "undefined" && typeof window !== "undefined") {
    performance.clearMarks(`querylane:${name}`);
    performance.mark(`querylane:${name}`);
    const attribute = `data-querylane-${name}`;
    if (!document.documentElement.hasAttribute(attribute)) document.documentElement.setAttribute(attribute, performance.now().toFixed(2));
  }
}
export function loadingMeasure(name: string, start: number) {
  if (typeof performance !== "undefined" && typeof window !== "undefined") {
    const label = `querylane:${name}`;
    performance.clearMeasures(label);
    performance.measure(label, { start, end: performance.now() });
  }
}
