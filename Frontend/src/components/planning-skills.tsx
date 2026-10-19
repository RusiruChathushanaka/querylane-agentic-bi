"use client";

import { useEffect, useId, useState } from "react";
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
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState("");
  const hintId = useId();
  useEffect(() => {
    const controller = new AbortController();
    void api<{ skills: SkillSummary[] }>("/skills", {
      signal: controller.signal,
    })
      .then((v) => {
        if (!controller.signal.aborted) setSkills(v.skills);
      })
      .catch((e) => {
        if (!controller.signal.aborted) setError(e.message);
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, []);
  const matchingSkills = skills.filter((skill) =>
    skill.name.toLowerCase().includes(query.trim().toLowerCase()),
  );
  return (
    <fieldset className="bi-wide bi-skills" aria-describedby={hintId}>
      <legend>
        Attached skills · <span aria-live="polite">{selected.length}/3</span>
      </legend>
      <p className="bi-note" id={hintId}>
        Optional. Choose up to three skills. The agent can also discover relevant
        skills. Versions are captured when you submit.
      </p>
      {error && <p role="alert">{error}</p>}
      {loading && (
        <p className="bi-note" role="status">
          Loading shared skills…
        </p>
      )}
      {!loading && !error && !skills.length && (
        <p className="bi-note">No shared skills available.</p>
      )}
      {!!skills.length && (
        <label className="bi-field bi-skills-search">
          <span>Find skills</span>
          <input
            type="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => {
              // Searching attachments must not implicitly submit a paid job.
              if (e.key === "Enter") e.preventDefault();
            }}
            placeholder="Search skill names"
          />
        </label>
      )}
      {!!skills.length && (
        <div
          className="bi-skills-options"
          role="region"
          aria-label="Available planning skills"
          tabIndex={0}
        >
          {matchingSkills.map((skill) => {
            const checked = selected.includes(skill.id);
            const compatible =
              skill.enabled &&
              !skill.deleted &&
              (source === "all" ||
                skill.source === "all" ||
                skill.source === source);
            return (
              <label key={skill.id} className="bi-skill-option">
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
                />
                <span>
                  {skill.name}
                  {!compatible && " — unavailable for this source"}
                </span>
              </label>
            );
          })}
          {!matchingSkills.length && (
            <p className="bi-note" role="status">
              No skills match your search.
            </p>
          )}
        </div>
      )}
    </fieldset>
  );
}
