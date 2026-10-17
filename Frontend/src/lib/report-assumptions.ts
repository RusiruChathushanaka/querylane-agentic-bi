import type { ForecastRequirement } from "./report-types";

export function assumptionHorizon(requirement: ForecastRequirement) {
  return requirement.horizon ?? { day: 28, week: 12, month: 3 }[requirement.grain];
}

// A single explicit value means the visitor assumes it stays constant.
// Blank, missing, nonfinite and wrongly sized inputs never become zero.
export function assumptionValues(text: string, horizon: number): number[] {
  const parts = text.trim().split(/[\s,;]+/);
  if (!text.trim() || parts.some((part) => !/^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?$/i.test(part)))
    throw new Error("Enter a number, or one number for each future period.");
  const values = parts.map(Number);
  if (values.some((value) => !Number.isFinite(value)))
    throw new Error("Assumptions must be finite numbers.");
  if (values.length === 1) return Array(horizon).fill(values[0]);
  if (values.length !== horizon)
    throw new Error(`Enter one constant value or exactly ${horizon} period values.`);
  return values;
}

export function assumptionRows(
  requirement: ForecastRequirement,
  entries: Record<string, string>,
) {
  const horizon = assumptionHorizon(requirement);
  const columns = requirement.drivers.map((driver) => assumptionValues(entries[driver] ?? "", horizon));
  return Array.from({ length: horizon }, (_, index) =>
    Object.fromEntries(requirement.drivers.map((driver, column) => [driver, columns[column][index]])),
  );
}
