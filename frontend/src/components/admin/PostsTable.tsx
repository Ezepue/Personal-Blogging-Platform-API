"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";

type Post = {
  id: number;
  title: string;
  status: string;
  published_date: string | null;
  author?: { username: string };
};

function Avatar({ name }: { name: string }) {
  const initials = name.slice(0, 2).toUpperCase();
  return (
    <span className="inline-flex items-center justify-center w-7 h-7 rounded-full bg-accent/20 text-accent text-xs font-bold shrink-0 select-none">
      {initials}
    </span>
  );
}

function StatusBadge({ status }: { status: string }) {
  const isPublished = status === "PUBLISHED";
  return (
    <span
      className={`inline-flex items-center gap-1.5 text-xs font-semibold rounded-full px-2.5 py-0.5 ${
        isPublished
          ? "bg-emerald-500/15 text-emerald-400 ring-1 ring-emerald-500/20"
          : "bg-border/60 text-muted ring-1 ring-border"
      }`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${isPublished ? "bg-emerald-400" : "bg-muted"}`} />
      {status}
    </span>
  );
}

function IconTrash() {
  return (
    <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" />
    </svg>
  );
}

function IconSearch() {
  return (
    <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 15.803 7.5 7.5 0 0015.803 15.803z" />
    </svg>
  );
}

function IconExternalLink() {
  return (
    <svg width="12" height="12" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 6H5.25A2.25 2.25 0 003 8.25v10.5A2.25 2.25 0 005.25 21h10.5A2.25 2.25 0 0018 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25" />
    </svg>
  );
}

function SkeletonRow() {
  return (
    <tr className="border-b border-border/40">
      {[1, 2, 3, 4, 5].map((i) => (
        <td key={i} className="py-3.5 pr-4">
          <div className="h-4 bg-border/50 rounded animate-pulse" style={{ width: `${[55, 20, 15, 15, 8][i - 1]}%` }} />
        </td>
      ))}
    </tr>
  );
}

function formatDate(dateStr: string | null) {
  if (!dateStr) return "—";
  const d = new Date(dateStr);
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}

export default function PostsTable() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/admin/articles");
      if (res.ok) {
        const data = await res.json();
        setPosts(Array.isArray(data) ? data : []);
      } else {
        setError("Failed to load posts");
      }
    } catch {
      setError("Network error — could not load posts");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const deletePost = async (id: number, title: string) => {
    if (!confirm(`Delete "${title}"? This cannot be undone.`)) return;
    setDeleting(id);
    setError(null);
    try {
      const res = await fetch(`/api/admin/articles/${id}`, { method: "DELETE" });
      if (res.ok) {
        await load();
      } else {
        const err = await res.json().catch(() => ({})) as { detail?: string };
        setError(err.detail ?? "Failed to delete post");
      }
    } catch {
      setError("Network error — could not delete post");
    } finally {
      setDeleting(null);
    }
  };

  const filtered = posts.filter((p) => {
    const q = search.toLowerCase();
    return (
      p.title.toLowerCase().includes(q) ||
      (p.author?.username ?? "").toLowerCase().includes(q)
    );
  });

  return (
    <div className="space-y-4">
      {/* Toolbar */}
      <div className="flex items-center justify-between gap-3">
        <div className="relative flex-1 max-w-xs">
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted pointer-events-none">
            <IconSearch />
          </span>
          <input
            type="text"
            placeholder="Search posts…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-3 py-2 bg-hover border border-border rounded-lg text-sm text-[#f1f1f5] placeholder:text-muted focus:outline-none focus:border-accent/60 transition-colors"
          />
        </div>
        <span className="text-muted text-xs shrink-0">
          {loading ? "Loading…" : `${filtered.length} of ${posts.length} post${posts.length !== 1 ? "s" : ""}`}
        </span>
      </div>

      {/* Error banner */}
      {error && (
        <div className="flex items-center gap-2 text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-4 py-3">
          <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} className="shrink-0">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
          </svg>
          {error}
          <button onClick={() => setError(null)} className="ml-auto text-red-400/60 hover:text-red-400 transition-colors">✕</button>
        </div>
      )}

      {/* Table */}
      <div className="overflow-x-auto -mx-1">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border text-left">
              <th className="pb-3 pr-4 text-xs font-semibold text-muted uppercase tracking-wider">Title</th>
              <th className="pb-3 pr-4 text-xs font-semibold text-muted uppercase tracking-wider">Author</th>
              <th className="pb-3 pr-4 text-xs font-semibold text-muted uppercase tracking-wider">Status</th>
              <th className="pb-3 pr-4 text-xs font-semibold text-muted uppercase tracking-wider">Published</th>
              <th className="pb-3 text-xs font-semibold text-muted uppercase tracking-wider text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              Array.from({ length: 4 }).map((_, i) => <SkeletonRow key={i} />)
            ) : filtered.length === 0 ? (
              <tr>
                <td colSpan={5} className="py-16 text-center">
                  <div className="flex flex-col items-center gap-2 text-muted">
                    <svg width="32" height="32" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.2} className="opacity-40">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
                    </svg>
                    <p className="text-sm">{search ? "No posts match your search" : "No posts yet"}</p>
                  </div>
                </td>
              </tr>
            ) : (
              filtered.map((p) => (
                <tr
                  key={p.id}
                  className="border-b border-border/40 hover:bg-hover/50 transition-colors group"
                >
                  <td className="py-3.5 pr-4 max-w-xs">
                    <Link
                      href={`/posts/${p.id}`}
                      className="flex items-center gap-1.5 text-[#f1f1f5] hover:text-accent transition-colors font-medium truncate"
                    >
                      <span className="truncate">{p.title}</span>
                      <span className="shrink-0 opacity-0 group-hover:opacity-100 transition-opacity text-muted">
                        <IconExternalLink />
                      </span>
                    </Link>
                  </td>
                  <td className="py-3.5 pr-4">
                    {p.author ? (
                      <div className="flex items-center gap-2">
                        <Avatar name={p.author.username} />
                        <span className="text-muted">{p.author.username}</span>
                      </div>
                    ) : (
                      <span className="text-muted/40">—</span>
                    )}
                  </td>
                  <td className="py-3.5 pr-4">
                    <StatusBadge status={p.status} />
                  </td>
                  <td className="py-3.5 pr-4 text-muted text-xs">
                    {formatDate(p.published_date)}
                  </td>
                  <td className="py-3.5 text-right">
                    <button
                      onClick={() => deletePost(p.id, p.title)}
                      disabled={deleting === p.id}
                      title="Delete post"
                      className="inline-flex items-center gap-1.5 text-xs text-muted hover:text-red-400 hover:bg-red-500/10 border border-transparent hover:border-red-500/20 rounded-md px-2.5 py-1.5 transition-all disabled:opacity-40 disabled:cursor-not-allowed"
                    >
                      <IconTrash />
                      {deleting === p.id ? "Deleting…" : "Delete"}
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
