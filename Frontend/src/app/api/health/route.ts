export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const response = await fetch(
      `${process.env.BACKEND_URL ?? "http://localhost:8000"}/health/live`,
      { cache: "no-store", signal: AbortSignal.timeout(5000) },
    );
    return Response.json(
      { status: response.ok ? "ready" : "degraded", backend: response.status },
      { status: response.ok ? 200 : 503 },
    );
  } catch {
    return Response.json(
      { status: "degraded", message: "Backend is unavailable." },
      { status: 503 },
    );
  }
}
