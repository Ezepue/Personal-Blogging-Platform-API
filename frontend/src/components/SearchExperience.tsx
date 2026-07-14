"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import PostCard, { Post } from "@/components/PostCard";
import VerifiedBadge from "@/components/VerifiedBadge";
import { avatarColor } from "@/lib/format";

type Author = { id: number; username: string; bio?: string | null; avatar_url?: string | null; is_verified?: boolean };

const RECENTS_KEY = "quill-recent-searches";

function loadRecents(): string[] {
  try {
    return JSON.parse(localStorage.getItem(RECENTS_KEY) || "[]");
  } catch {
    return [];
  }
}

/** Client search UI: input with recent-search chips, plus highlighted results. */
export default function SearchExperience({
  query,
  articles,
  authors,
}: {
  query: string;
  articles: Post[];
  authors: Author[];
}) {
  const router = useRouter();
  const [value, setValue] = useState(query);
  const [recents, setRecents] = useState<string[]>([]);

  useEffect(() => setRecents(loadRecents()), []);

  // Record a completed search (there are server-rendered results for it).
  useEffect(() => {
    if (!query.trim()) return;
    const next = [query, ...loadRecents().filter((r) => r !== query)].slice(0, 6);
    localStorage.setItem(RECENTS_KEY, JSON.stringify(next));
    setRecents(next);
  }, [query]);

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (value.trim()) router.push(`/search?q=${encodeURIComponent(value.trim())}`);
  };

  const clearRecents = () => {
    localStorage.removeItem(RECENTS_KEY);
    setRecents([]);
  };

  return (
    <>
      <form onSubmit={submit} className="mb-6">
        <div className="relative">
          <input
            type="text"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            placeholder="Titles, ideas, writers…  (try author:name or tag:name)"
            autoFocus
            className="w-full bg-surface border border-border rounded-full px-6 py-4 pr-14 text-lg text-ink placeholder:text-muted focus:outline-none focus:border-accent transition-colors shadow-soft"
          />
          <button type="submit" aria-label="Search" className="absolute right-2 top-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-accent hover:bg-accent-hover text-white transition-colors flex items-center justify-center">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              <circle cx="11" cy="11" r="7" /><path d="m21 21-4.3-4.3" />
            </svg>
          </button>
        </div>
      </form>

      {!query && recents.length > 0 && (
        <div className="mb-10">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs uppercase tracking-widest text-muted">Recent searches</span>
            <button onClick={clearRecents} className="text-xs text-muted hover:text-ink transition-colors">Clear</button>
          </div>
          <div className="flex flex-wrap gap-2">
            {recents.map((r) => (
              <Link key={r} href={`/search?q=${encodeURIComponent(r)}`} className="text-sm px-4 py-1.5 rounded-full border border-border bg-surface text-muted hover:text-accent hover:border-accent transition-colors">
                {r}
              </Link>
            ))}
          </div>
        </div>
      )}

      {query && (
        <>
          {authors.length > 0 && (
            <section className="mb-12">
              <h2 className="text-xs uppercase tracking-widest text-muted mb-4">Writers</h2>
              <div className="grid sm:grid-cols-2 gap-4">
                {authors.map((a) => (
                  <Link key={a.id} href={`/profile/${a.username}`} className="card-lift bg-surface border border-border rounded-2xl p-4 flex items-center gap-3 shadow-soft">
                    <span className="w-10 h-10 rounded-full flex items-center justify-center font-bold text-white overflow-hidden shrink-0" style={a.avatar_url ? undefined : { backgroundColor: avatarColor(a.username) }}>
                      {a.avatar_url ? (
                        // eslint-disable-next-line @next/next/no-img-element
                        <img src={a.avatar_url} alt={a.username} className="w-full h-full object-cover" />
                      ) : (
                        a.username[0]?.toUpperCase()
                      )}
                    </span>
                    <span className="min-w-0">
                      <span className="flex items-center gap-1 text-ink font-medium">{highlight(a.username, query)}{a.is_verified && <VerifiedBadge />}</span>
                      {a.bio && <span className="block text-muted text-sm truncate">{a.bio}</span>}
                    </span>
                  </Link>
                ))}
              </div>
            </section>
          )}

          <section>
            <h2 className="text-xs uppercase tracking-widest text-muted mb-4">
              Stories {articles.length > 0 && `(${articles.length})`}
            </h2>
            {articles.length === 0 ? (
              <p className="text-muted py-12 text-center">Nothing found for “{query}”. Try a different phrase.</p>
            ) : (
              <div className="space-y-6">
                {articles.map((post) => <PostCard key={post.id} post={post} />)}
              </div>
            )}
          </section>
        </>
      )}
    </>
  );
}

/** Wrap case-insensitive matches of the plain search terms in <mark>. */
function highlight(text: string, query: string) {
  const terms = query
    .split(/\s+/)
    .filter((t) => !t.includes(":"))
    .map((t) => t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"))
    .filter(Boolean);
  if (terms.length === 0) return text;
  const parts = text.split(new RegExp(`(${terms.join("|")})`, "ig"));
  return parts.map((part, i) =>
    terms.some((t) => new RegExp(`^${t}$`, "i").test(part)) ? (
      <mark key={i} className="bg-accent-soft text-accent rounded px-0.5">{part}</mark>
    ) : (
      <span key={i}>{part}</span>
    ),
  );
}
