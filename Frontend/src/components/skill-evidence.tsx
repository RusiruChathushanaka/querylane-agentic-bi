import Link from "next/link";
import { BookOpen } from "lucide-react";
import type { SkillReference } from "@/lib/types";

export function SkillEvidence({
  skills = [],
  warnings = [],
}: {
  skills?: SkillReference[];
  warnings?: string[];
}) {
  if (!skills.length && !warnings.length) return null;
  return (
    <div className="skill-evidence">
      {skills.length > 0 && (
        <>
          <span>
            <BookOpen aria-hidden /> Skills used
          </span>
          <ul>
            {skills.map((skill) => (
              <li key={skill.id}>
                <Link href={`/skills/${skill.id}/revisions/${skill.revision}`}>
                  {skill.name}{" "}
                  <small>
                    v{skill.revision} ·{" "}
                    {skill.mode === "manual" ? "Attached" : "Automatic"}
                  </small>
                </Link>
              </li>
            ))}
          </ul>
        </>
      )}
      {warnings.map((warning) => (
        <p key={warning}>{warning}</p>
      ))}
    </div>
  );
}
