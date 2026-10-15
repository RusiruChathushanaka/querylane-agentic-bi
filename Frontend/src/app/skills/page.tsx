import type { Metadata } from "next";
import { SkillsWorkspace } from "@/components/skills-workspace";

export const metadata: Metadata = { title: "Skills — Querylane" };

export default function SkillsPage() {
  return <SkillsWorkspace />;
}
