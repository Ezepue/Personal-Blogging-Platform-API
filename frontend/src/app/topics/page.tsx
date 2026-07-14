import Link from "next/link";
import type { Metadata } from "next";

const API_URL = process.env.API_URL ?? "http://localhost:8000";

export const metadata: Metadata = { title: "Topics" };
export const revalidate = 300;

type TagCount = { tag: string; count: number };

async function getTags(): Promise<TagCount[]> {
  try {
    const res = await fetch(`${API_URL}/articles/tags?limit=100`, {
      next: { revalidate: 300 },
    });
    return res.ok ? res.json() : [];
  } catch {
    return [];
  }
}

export default async function TopicsPage() {
  const tags = await getTags();
  const max = Math.max(1, ...tags.map((t) => t.count));

  return (
    <div className="max-w-4xl mx-auto">
      <div className="relative overflow-hidden -mx-4 sm:-mx-6 px-4 sm:px-6 pt-10 pb-8 mb-8">
        <div className="art-field" aria-hidden />
        <h1 className="relative font-display text-5xl text-ink fade-up">
          Browse by <span className="display-italic">topic</span>
        </h1>
        <p className="relative text-muted mt-3 max-w-lg fade-up fade-up-1">
          Every tag used across published stories. The bigger the type, the busier the topic.
        </p>
      </div>

      {tags.length === 0 ? (
        <p className="text-muted text-center py-20">No topics yet — publish the first story.</p>
      ) : (
        <div className="flex flex-wrap items-baseline gap-x-6 gap-y-4 fade-up fade-up-2">
          {tags.map(({ tag, count }) => {
            // scale type size by usage: 1rem → 2.6rem
            const size = 1 + (count / max) * 1.6;
            return (
              <Link
                key={tag}
                href={`/topics/${encodeURIComponent(tag)}`}
                className="font-display text-ink-soft hover:text-accent transition-colors leading-none"
                style={{ fontSize: `${size}rem` }}
              >
                {tag}
                <sup className="text-xs text-muted ml-1">{count}</sup>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
