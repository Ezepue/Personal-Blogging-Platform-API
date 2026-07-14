import Link from "next/link";
import PostCard, { Post } from "@/components/PostCard";
import type { Metadata } from "next";

const API_URL = process.env.API_URL ?? "http://localhost:8000";

export const metadata: Metadata = { title: "Search" };
export const dynamic = "force-dynamic";

type Author = { id: number; username: string; bio?: string | null; avatar_url?: string | null };

async function search(q: string): Promise<{ articles: Post[]; authors: Author[] }> {
  if (!q.trim()) return { articles: [], authors: [] };
  try {
    const res = await fetch(`${API_URL}/articles/search?q=${encodeURIComponent(q)}&limit=30`, {
      cache: "no-store",
    });
    return res.ok ? res.json() : { articles: [], authors: [] };
  } catch {
    return { articles: [], authors: [] };
  }
}

export default async function SearchPage({
  searchParams,
}: {
  searchParams: { q?: string };
}) {
  const q = searchParams.q ?? "";
  const { articles, authors } = await search(q);

  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="font-display text-4xl text-ink mb-8">
        Search the <span className="display-italic">archive</span>
      </h1>

      {/* Search form (GET → server-rendered results) */}
      <form action="/search" method="get" className="mb-12">
        <div className="relative">
          <input
            type="text"
            name="q"
            defaultValue={q}
            placeholder="Titles, ideas, writers…"
            autoFocus
            className="w-full bg-surface border border-border rounded-full px-6 py-4 pr-14 text-lg text-ink placeholder:text-muted focus:outline-none focus:border-accent transition-colors shadow-soft"
          />
          <button
            type="submit"
            aria-label="Search"
            className="absolute right-2 top-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-accent hover:bg-accent-hover text-white transition-colors flex items-center justify-center"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              <circle cx="11" cy="11" r="7" />
              <path d="m21 21-4.3-4.3" />
            </svg>
          </button>
        </div>
      </form>

      {q && (
        <>
          {/* Writers */}
          {authors.length > 0 && (
            <section className="mb-12">
              <h2 className="text-xs uppercase tracking-widest text-muted mb-4">Writers</h2>
              <div className="grid sm:grid-cols-2 gap-4">
                {authors.map((a) => (
                  <Link
                    key={a.id}
                    href={`/profile/${a.username}`}
                    className="card-lift bg-surface border border-border rounded-2xl p-4 flex items-center gap-3 shadow-soft"
                  >
                    <span className="w-10 h-10 rounded-full bg-accent-soft flex items-center justify-center font-bold text-accent overflow-hidden shrink-0">
                      {a.avatar_url ? (
                        // eslint-disable-next-line @next/next/no-img-element
                        <img src={a.avatar_url} alt={a.username} className="w-full h-full object-cover" />
                      ) : (
                        a.username[0]?.toUpperCase()
                      )}
                    </span>
                    <span className="min-w-0">
                      <span className="block text-ink font-medium">{a.username}</span>
                      {a.bio && <span className="block text-muted text-sm truncate">{a.bio}</span>}
                    </span>
                  </Link>
                ))}
              </div>
            </section>
          )}

          {/* Stories */}
          <section>
            <h2 className="text-xs uppercase tracking-widest text-muted mb-4">
              Stories {articles.length > 0 && `(${articles.length})`}
            </h2>
            {articles.length === 0 ? (
              <p className="text-muted py-12 text-center">
                Nothing found for “{q}”. Try a different phrase.
              </p>
            ) : (
              <div className="space-y-6">
                {articles.map((post) => (
                  <PostCard key={post.id} post={post} />
                ))}
              </div>
            )}
          </section>
        </>
      )}
    </div>
  );
}
