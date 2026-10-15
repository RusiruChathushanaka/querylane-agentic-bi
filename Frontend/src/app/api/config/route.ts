export const dynamic = "force-dynamic";

export async function GET() {
  return Response.json(
    { backend_url: process.env.BACKEND_URL ?? "http://localhost:8000" },
    { headers: { "Cache-Control": "no-store" } },
  );
}
