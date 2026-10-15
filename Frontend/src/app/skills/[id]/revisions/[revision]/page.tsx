import type { Metadata } from "next";
import { SkillRevision } from "@/components/skill-revision";

export const metadata: Metadata = { title: "Skill version — Querylane" };

export default async function RevisionPage({
  params,
}: {
  params: Promise<{ id: string; revision: string }>;
}) {
  const { id, revision } = await params;
  return <SkillRevision id={id} revision={revision} />;
}
