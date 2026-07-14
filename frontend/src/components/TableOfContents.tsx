"use client";

import { useEffect, useState } from "react";

type Heading = { id: string; text: string; level: number };

// Builds a table of contents from the rendered article's h2/h3 headings,
// assigning ids so entries can anchor-link into the text.
export default function TableOfContents({ containerId }: { containerId: string }) {
  const [headings, setHeadings] = useState<Heading[]>([]);
  const [active, setActive] = useState<string>("");

  useEffect(() => {
    const container = document.getElementById(containerId);
    if (!container) return;

    const nodes = Array.from(container.querySelectorAll<HTMLElement>("h1, h2, h3"));
    const found: Heading[] = nodes.map((node, i) => {
      if (!node.id) {
        const slug =
          (node.textContent ?? "")
            .toLowerCase()
            .replace(/[^a-z0-9]+/g, "-")
            .replace(/(^-|-$)/g, "")
            .slice(0, 60) || `section-${i}`;
        node.id = `${slug}-${i}`;
      }
      return {
        id: node.id,
        text: node.textContent ?? "",
        level: node.tagName === "H3" ? 3 : 2,
      };
    });
    setHeadings(found);

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            setActive(entry.target.id);
            break;
          }
        }
      },
      { rootMargin: "-15% 0px -70% 0px" }
    );
    nodes.forEach((n) => observer.observe(n));
    return () => observer.disconnect();
  }, [containerId]);

  if (headings.length < 2) return null;

  return (
    <nav aria-label="Table of contents" className="hidden xl:block sticky top-28 max-h-[70vh] overflow-y-auto pr-2">
      <p className="text-xs uppercase tracking-widest text-muted mb-4">Contents</p>
      <ul className="space-y-2.5 text-sm border-l border-border">
        {headings.map((h) => (
          <li key={h.id} className={h.level === 3 ? "pl-7" : "pl-4"}>
            <a
              href={`#${h.id}`}
              className={`block leading-snug transition-colors -ml-px border-l-2 pl-3 ${
                active === h.id
                  ? "border-accent text-ink"
                  : "border-transparent text-muted hover:text-ink"
              }`}
            >
              {h.text}
            </a>
          </li>
        ))}
      </ul>
    </nav>
  );
}
