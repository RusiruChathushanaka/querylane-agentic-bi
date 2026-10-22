"use client";
import { useReadResource } from "@/hooks/use-read-resource";
import { ResourceFeedback } from "./resource-feedback";

import { useState } from "react";
import Link from "next/link";
import { ArrowLeft, BookOpen } from "lucide-react";
import { api } from "@/lib/api";
import type { Skill } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { SkillMarkdown } from "@/components/skill-markdown";

export function SkillRevision({
  id,
  revision,
}: {
  id: string;
  revision: string;
}) {
  const [skill, setSkill] = useState<Skill>();
  const resource = useReadResource(`${id}:${revision}`, (signal) => api<Skill>(`/skills/${encodeURIComponent(id)}/revisions/${encodeURIComponent(revision)}`, { signal }), setSkill);
  return (
    <div className="skills-shell">
      <a className="skip-link" href="#skill-version">
        Skip to skill version
      </a>
      <header className="skills-header">
        <Link href="/skills" className="skills-brand">
          <BookOpen aria-hidden /> Querylane<span>.</span>
        </Link>
        <Button variant="outline" asChild>
          <Link href="/skills">
            <ArrowLeft aria-hidden /> Skills library
          </Link>
        </Button>
      </header>
      <main
        id="skill-version"
        tabIndex={-1}
        className="skills-main skill-version"
      >
        <p className="welcome-eyebrow">IMMUTABLE SKILL VERSION</p>
        <ResourceFeedback resource={resource} label="Loading saved skill version" />
        {!skill ? (
          resource.pending ? <Skeleton aria-hidden="true" className="h-40" /> : null
        ) : (
          <>
            <h1>
              {skill.name}
              <span>.</span>
            </h1>
            <p className="skills-intro">
              Version {skill.revision} ·{" "}
              {new Date(skill.updated_at).toLocaleString()} · Public
            </p>
            <p>{skill.description}</p>
            <dl className="skill-version-meta">
              <dt>When to use</dt>
              <dd>{skill.when_to_use}</dd>
              <dt>Source</dt>
              <dd>
                {skill.source === "all"
                  ? "All sources"
                  : skill.source === "postgres"
                    ? "PostgreSQL"
                    : "BigQuery"}
              </dd>
            </dl>
            <p className="skills-public-note">
              This is the saved version used as evidence. Later edits and
              deletion do not change it.
            </p>
            <SkillMarkdown headingLevel={2}>{skill.instructions}</SkillMarkdown>
          </>
        )}
      </main>
    </div>
  );
}
