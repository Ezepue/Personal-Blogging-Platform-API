"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";

type ArticleStats = {
  id: number;
  title: string;
  status: string;
  published_date?: string | null;
  views_count: number;
  likes_count: number;
  comments_count: number;
};

type Stats = {
  total_articles: number;
  total_published: number;
  total_drafts: number;
  total_views: number;
  total_likes: number;
  total_comments: number;
  followers_count: number;
  following_count: number;
  articles: ArticleStats[];
};

// Compact display figures: 1,284 / 12.9K / 4.2M
function compact(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1).replace(/\.0$/, "")}M`;
  if (n >= 10_000) return `${(n / 1_000).toFixed(1).replace(/\.0$/, "")}K`;
  return n.toLocaleString("en-US");
}

function StatTile({ label, value }: { label: string; value: number }) {
  return (
    <div className="bg-surface border border-border rounded-2xl p-5 shadow-soft">
      <p className="text-sm text-muted mb-1">{label}</p>
      <p className="text-3xl font-semibold text-ink">{compact(value)}</p>
    </div>
  );
}

export default function DashboardPage() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const [stats, setStats] = useState<Stats | null>(null);
  const [fetching, setFetching] = useState(true);

  useEffect(() => {
    if (!loading && !user) router.push("/login");
  }, [user, loading, router]);

  useEffect(() => {
    if (!user) return;
    fetch("/api/dashboard/")
      .then((r) => (r.ok ? r.json() : null))
      .then(setStats)
      .catch(() => {})
      .finally(() => setFetching(false));
  }, [user]);

  if (loading || !user) return null;

  return (
    <div className="max-w-5xl mx-auto">
      <p className="text-xs uppercase tracking-[0.3em] text-muted mb-3 fade-up">Your studio</p>
      <h1 className="font-display text-5xl text-ink mb-10 fade-up">
        Writer’s <span className="display-italic">dashboard</span>
      </h1>

      {fetching || !stats ? (
        <div className="flex items-center justify-center min-h-[30vh]">
          <div className="w-8 h-8 border-2 border-accent border-t-transparent rounded-full animate-spin" />
        </div>
      ) : (
        <>
          {/* KPI row */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-10 fade-up fade-up-1">
            <StatTile label="Views" value={stats.total_views} />
            <StatTile label="Likes" value={stats.total_likes} />
            <StatTile label="Comments" value={stats.total_comments} />
            <StatTile label="Followers" value={stats.followers_count} />
            <StatTile label="Published" value={stats.total_published} />
            <StatTile label="Drafts" value={stats.total_drafts} />
          </div>

          {/* Per-story table */}
          <div className="bg-surface border border-border rounded-2xl shadow-soft overflow-hidden fade-up fade-up-2">
            <div className="px-6 py-4 border-b border-border flex items-center justify-between">
              <h2 className="text-ink font-medium">Stories</h2>
              <Link href="/write" className="text-sm text-accent hover:underline">
                Write a new story →
              </Link>
            </div>
            {stats.articles.length === 0 ? (
              <p className="text-muted text-sm text-center py-14">
                No stories yet — your stats will appear here once you publish.
              </p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-left text-xs uppercase tracking-wider text-muted border-b border-border">
                      <th className="px-6 py-3 font-medium">Title</th>
                      <th className="px-4 py-3 font-medium">Status</th>
                      <th className="px-4 py-3 font-medium text-right">Views</th>
                      <th className="px-4 py-3 font-medium text-right">Likes</th>
                      <th className="px-4 py-3 font-medium text-right">Comments</th>
                      <th className="px-6 py-3 font-medium text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {stats.articles.map((a) => (
                      <tr key={a.id} className="border-b border-border last:border-0 hover:bg-raised transition-colors">
                        <td className="px-6 py-3.5 max-w-[280px]">
                          <Link href={`/posts/${a.id}`} className="text-ink hover:text-accent transition-colors line-clamp-1">
                            {a.title}
                          </Link>
                        </td>
                        <td className="px-4 py-3.5">
                          <span
                            className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                              a.status === "published"
                                ? "bg-accent-soft text-accent"
                                : "bg-raised text-muted border border-border"
                            }`}
                          >
                            {a.status}
                          </span>
                        </td>
                        <td className="px-4 py-3.5 text-right text-ink-soft tabular-nums">{a.views_count.toLocaleString()}</td>
                        <td className="px-4 py-3.5 text-right text-ink-soft tabular-nums">{a.likes_count.toLocaleString()}</td>
                        <td className="px-4 py-3.5 text-right text-ink-soft tabular-nums">{a.comments_count.toLocaleString()}</td>
                        <td className="px-6 py-3.5 text-right">
                          <Link href={`/write/${a.id}`} className="text-muted hover:text-accent transition-colors">
                            Edit
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
