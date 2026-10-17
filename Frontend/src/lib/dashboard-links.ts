export function dashboardPath(id: string, mode: "view" | "edit" = "view") {
  const path = `/dashboards/${encodeURIComponent(id)}`;
  return mode === "edit" ? `${path}?mode=edit` : path;
}

export function dashboardShareUrl(origin: string, id: string) {
  return new URL(dashboardPath(id), origin).href;
}
