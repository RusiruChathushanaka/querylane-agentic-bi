"use client";

import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import "@/app/markdown.css";

export function MarkdownContent({
  children,
  className = "",
  headingLevel = 3,
}: {
  children: string;
  className?: string;
  headingLevel?: 2 | 3;
}) {
  const Heading = headingLevel === 2 ? "h2" : "h3";
  return (
    <div className={`markdown-content ${className}`}>
      <Markdown
        remarkPlugins={[remarkGfm]}
        skipHtml
        disallowedElements={[
          "img",
          "iframe",
          "video",
          "audio",
          "source",
          "object",
          "embed",
          "script",
          "style",
        ]}
        components={{
          h1: ({ children }) => <Heading>{children}</Heading>,
          h2: ({ children }) => <Heading>{children}</Heading>,
          h3: ({ children }) => <Heading>{children}</Heading>,
          h4: ({ children }) => <Heading>{children}</Heading>,
          h5: ({ children }) => <Heading>{children}</Heading>,
          h6: ({ children }) => <Heading>{children}</Heading>,
          a: ({ href, children }) => (
            <a href={href} rel="noopener noreferrer" target="_blank">
              {children}
            </a>
          ),
          table: ({ children }) => (
            <div
              className="markdown-table-scroll"
              role="region"
              aria-label="Markdown table"
              tabIndex={0}
            >
              <table>{children}</table>
            </div>
          ),
          pre: ({ children }) => (
            <pre role="region" tabIndex={0} aria-label="Code block">
              {children}
            </pre>
          ),
          input: ({ checked }) => (
            <input
              type="checkbox"
              checked={Boolean(checked)}
              disabled
              aria-label={checked ? "Completed task" : "Incomplete task"}
            />
          ),
        }}
      >
        {children}
      </Markdown>
    </div>
  );
}

export function MessageContent({
  role,
  children,
  className = "",
}: {
  role: "user" | "assistant";
  children: string;
  className?: string;
}) {
  return role === "assistant" ? (
    <MarkdownContent className={className} headingLevel={2}>
      {children}
    </MarkdownContent>
  ) : (
    <p className={className}>{children}</p>
  );
}
