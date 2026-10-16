"use client";

import { MarkdownContent } from "@/components/markdown-content";

export function SkillMarkdown({
  children,
  headingLevel = 3,
}: {
  children: string;
  headingLevel?: 2 | 3;
}) {
  return (
    <MarkdownContent className="skill-markdown" headingLevel={headingLevel}>
      {children}
    </MarkdownContent>
  );
}
