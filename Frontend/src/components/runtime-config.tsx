import { connection } from "next/server";
import { RuntimeBootstrap } from "./runtime-bootstrap";

/** Request-time public config only. Never wait for a backend, guest session or source. */
export async function RuntimeConfig({ children }: { children: React.ReactNode }) {
  await connection();
  return <RuntimeBootstrap backendUrl={process.env.BACKEND_URL ?? "http://localhost:8000"}>{children}</RuntimeBootstrap>;
}
