"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { SkillSummary } from "@/lib/types";

/** Attachments remain local until the application captures an immutable job brief. */
export function PlanningSkills({
  source,
  selected,
  onChange,
}: {
  source: string;
  selected: string[];
  onChange: (ids: string[]) => void;
}) {
  const [skills, setSkills] = useState<SkillSummary[]>([]);
  const [error, setError] = useState("");
  useEffect(() => {
    const controller = new AbortController();
    void api<{ skills: SkillSummary[] }>("/skills", {
      signal: controller.signal,
    })
      .then((v) => setSkills(v.skills))
      .catch((e) => {
        if (!controller.signal.aborted) setError(e.message);
      });
    return () => controller.abort();
  }, []);
  return (
    <fieldset className="bi-wide">
      <legend>Attached skills · {selected.length}/3</legend>
      <p className="bi-note">
        Optional. The agent can also discover relevant skills. Versions are
        captured when you submit.
      </p>
      {error && <p role="alert">{error}</p>}
      {!error && !skills.length && (
        <p className="bi-note">No shared skills available.</p>
      )}
      <div className="bi-actions">
        {skills.map((skill) => {
          const checked = selected.includes(skill.id);
          const compatible =
            skill.enabled &&
            !skill.deleted &&
            (source === "all" ||
              skill.source === "all" ||
              skill.source === source);
          return (
            <label key={skill.id} className="bi-card">
              <input
                type="checkbox"
                checked={checked}
                disabled={!checked && (!compatible || selected.length >= 3)}
                onChange={() =>
                  onChange(
                    checked
                      ? selected.filter((id) => id !== skill.id)
                      : [...selected, skill.id],
                  )
                }
              />{" "}
              {skill.name}
              {!compatible && " — unavailable for this source"}
            </label>
          );
        })}
      </div>
    </fieldset>
  );
}
