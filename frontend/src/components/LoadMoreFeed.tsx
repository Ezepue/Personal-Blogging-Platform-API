"use client";

import { useState } from "react";
import PostCard, { Post } from "@/components/PostCard";

/**
 * Renders the feed grid and appends further pages on demand.
 * The first page is server-rendered and passed in as `initial`.
 */
export default function LoadMoreFeed({
  initial,
  sort,
  total,
}: {
  initial: Post[];
  sort: string;
  total: number;
}) {
  const [posts, setPosts] = useState<Post[]>(initial);
  const [loading, setLoading] = useState(false);
  const hasMore = posts.length < total;

  const loadMore = async () => {
    setLoading(true);
    try {
      const res = await fetch(`/api/articles?sort=${sort}&skip=${posts.length}&limit=12`);
      if (res.ok) {
        const next: Post[] = await res.json();
        // Dedup by id: the list can shift between the cached first page and this
        // live fetch, so a story could arrive twice (duplicate React keys).
        setPosts((prev) => {
          const seen = new Set(prev.map((p) => p.id));
          return [...prev, ...next.filter((p) => !seen.has(p.id))];
        });
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {posts.map((post, i) => (
          <div key={post.id} className={`fade-up ${i < 3 ? `fade-up-${i + 1}` : ""}`}>
            <PostCard post={post} />
          </div>
        ))}
      </div>
      {hasMore && (
        <div className="flex justify-center mt-10">
          <button
            onClick={loadMore}
            disabled={loading}
            className="px-6 py-3 rounded-full border border-border text-ink-soft hover:text-ink hover:border-ink transition-colors disabled:opacity-50"
          >
            {loading ? "Loading…" : "Load more stories"}
          </button>
        </div>
      )}
    </>
  );
}
