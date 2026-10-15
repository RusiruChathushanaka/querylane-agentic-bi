"use client";

import Markdown from "react-markdown";

export function SkillMarkdown({
  children,
  headingLevel = 3,
}: {
  children: string;
  headingLevel?: 2 | 3;
}) {
  const Heading = headingLevel === 2 ? "h2" : "h3";
  return (
    <div className="skill-markdown">
      <Markdown
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
        }}
      >
        {children}
      </Markdown>
    </div>
  );
}
