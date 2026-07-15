import Link from "next/link";
import { cookies } from "next/headers";
import PostCard, { Post } from "@/components/PostCard";
import LoadMoreFeed from "@/components/LoadMoreFeed";
import Greeting from "@/components/Greeting";

const API_URL = process.env.API_URL ?? "http://localhost:8000";

export const dynamic = "force-dynamic";

type TagCount = { tag: string; count: number };

async function getFeatured(): Promise<Post[]> {
  try {
    const res = await fetch(`${API_URL}/articles/featured?limit=3`, { next: { revalidate: 120 } });
    return res.ok ? res.json() : [];
  } catch {
    return [];
  }
}

async function getFeedPage(tab: string): Promise<{ posts: Post[]; total: number }> {
  try {
    if (tab === "following") {
      const token = cookies().get("access_token")?.value;
      if (!token) return { posts: [], total: 0 };
      const res = await fetch(`${API_URL}/articles/feed?limit=24`, {
        headers: { Authorization: `Bearer ${token}` },
        cache: "no-store",
      });
      const posts = res.ok ? await res.json() : [];
      return { posts, total: posts.length };
    }
    const res = await fetch(`${API_URL}/articles?sort=${tab}&limit=12`, { next: { revalidate: 60 } });
    const posts = res.ok ? await res.json() : [];
    const total = Number(res.headers.get("x-total-count") ?? posts.length);
    return { posts, total };
  } catch {
    return { posts: [], total: 0 };
  }
}

const TABS = [
  { key: "latest", label: "Latest" },
  { key: "trending", label: "Trending" },
  { key: "top", label: "Most loved" },
  { key: "following", label: "Following" },
] as const;

async function getTags(): Promise<TagCount[]> {
  try {
    const res = await fetch(`${API_URL}/articles/tags?limit=12`, {
      next: { revalidate: 300 },
    });
    return res.ok ? res.json() : [];
  } catch {
    return [];
  }
}

export default async function Home({
  searchParams,
}: {
  searchParams: { tab?: string };
}) {
  const tab = TABS.some((t) => t.key === searchParams.tab) ? searchParams.tab! : "latest";
  const [{ posts, total }, tags, featured] = await Promise.all([
    getFeedPage(tab),
    getTags(),
    tab === "latest" ? getFeatured() : Promise.resolve([]),
  ]);

  return (
    <div className="relative">
      {/* Hero */}
      <section className="relative -mx-4 sm:-mx-6 px-4 sm:px-6 pt-14 pb-12 mb-10 overflow-hidden">
        <div className="art-field" aria-hidden />
        <div className="relative max-w-3xl fade-up">
          <Greeting />
          <p className="text-xs uppercase tracking-[0.3em] text-muted mb-5">
            A quiet place for loud ideas
          </p>
          <h1 className="font-display text-5xl sm:text-6xl md:text-7xl leading-[1.05] text-ink">
            Stories worth <span className="display-italic">reading</span>,
            <br />
            written with <span className="display-italic">care</span>.
          </h1>
          <p className="mt-6 text-lg text-muted max-w-xl leading-relaxed">
            Essays, notes, and ideas from writers who take their time. Follow the
            voices you love and keep a reading list of your own.
          </p>
          <div className="mt-8 flex items-center gap-4">
            <Link
              href="/write"
              className="bg-accent hover:bg-accent-hover text-white px-6 py-3 rounded-full font-medium transition-colors"
            >
              Start writing
            </Link>
            <Link href="/topics" className="link-flourish text-ink-soft hover:text-ink transition-colors py-3">
              Browse topics →
            </Link>
          </div>
        </div>
      </section>

      {/* Topic rail */}
      {tags.length > 0 && (
        <div className="flex gap-2 overflow-x-auto pb-2 mb-10 fade-up fade-up-1">
          {tags.map(({ tag, count }) => (
            <Link
              key={tag}
              href={`/topics/${encodeURIComponent(tag)}`}
              className="whitespace-nowrap text-sm px-4 py-1.5 rounded-full border border-border bg-surface text-muted hover:text-accent hover:border-accent transition-colors"
            >
              {tag} <span className="opacity-60">{count}</span>
            </Link>
          ))}
        </div>
      )}

      {/* Editors' picks */}
      {featured.length > 0 && (
        <section className="mb-12 fade-up fade-up-1">
          <h2 className="text-xs uppercase tracking-[0.3em] text-muted mb-4">Editors’ picks</h2>
          <div className="grid md:grid-cols-3 gap-6">
            {featured.map((post) => <PostCard key={post.id} post={post} />)}
          </div>
        </section>
      )}

      {/* Feed tabs */}
      <div className="flex items-center gap-1 border-b border-border mb-10 fade-up fade-up-2 overflow-x-auto">
        {TABS.map((t) => (
          <Link
            key={t.key}
            href={t.key === "latest" ? "/" : `/?tab=${t.key}`}
            className={`px-4 py-3 text-sm font-medium -mb-px border-b-2 whitespace-nowrap transition-colors ${
              tab === t.key ? "border-accent text-ink" : "border-transparent text-muted hover:text-ink"
            }`}
          >
            {t.label}
          </Link>
        ))}
      </div>

      {/* Feed */}
      {posts.length === 0 ? (
        <div className="text-center py-24 fade-up">
          <p className="font-display text-2xl text-ink mb-2">
            {tab === "following" ? "Your feed is quiet" : "Nothing here yet"}
          </p>
          <p className="text-muted text-sm">
            {tab === "following"
              ? "Follow some writers and their stories will appear here."
              : "Be the first to publish a story."}
          </p>
        </div>
      ) : tab === "following" ? (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {posts.map((post, i) => (
            <div key={post.id} className={`fade-up ${i < 3 ? `fade-up-${i + 1}` : ""}`}>
              <PostCard post={post} />
            </div>
          ))}
        </div>
      ) : (
        <LoadMoreFeed initial={posts} sort={tab} total={total} />
      )}
    </div>
  );
}
