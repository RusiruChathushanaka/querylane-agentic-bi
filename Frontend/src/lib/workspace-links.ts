/** One canonical route for new, shared, forked, and source conversations. */
export function workspacePath(conversationId?: string, search = ""): string {
  if (!conversationId) return "/app";
  const params = new URLSearchParams(search);
  params.set("chat", conversationId);
  return `/app?${params}`;
}
