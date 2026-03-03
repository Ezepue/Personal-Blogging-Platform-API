"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";

type Comment = {
  id: number;
  content: string;
  created_date: string;
  user?: { username: string };
  article_id?: number;
};

function Avatar({ name }: { name: string }) {
  return (
    <span className="inline-flex items-center justify-center w-7 h-7 rounded-full bg-accent/20 text-accent text-xs font-bold shrink-0 select-none">
      {name.slice(0, 2).toUpperCase()}
    </span>
  );
}

function IconSearch() {
  return (
    <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 15.803 7.5 7.5 0 0015.803 15.803z" />
    </svg>
  );
}

function IconTrash() {
  return (
    <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" />
    </svg>
  );
}

function IconError() {
  return (
    <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} className="shrink-0">
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
    </svg>
  );
}

function IconExternalLink() {
  return (
    <svg width="11" height="11" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 6H5.25A2.25 2.25 0 003 8.25v10.5A2.25 2.25 0 005.25 21h10.5A2.25 2.25 0 0018 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25" />
    </svg>
  );
}

function SkeletonRow() {
  return (
    <tr className="border-b border-border/40">
      {[55, 20, 15, 8].map((w, i) => (
        <td key={i} className="py-3.5 pr-4">
          <div className="h-4 bg-border/50 rounded animate-pulse" style={{ width: `${w}%` }} />
        </td>
      ))}
    </tr>
  );
}

function formatDate(dateStr: string) {
  if (!dateStr) return "—";
  const d = new Date(dateStr);
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}

export default function CommentsTable() {
  const [comments, setComments] = useState<Comment[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/admin/comments");
      if (res.ok) {
        const data = await res.json();
        setComments(Array.isArray(data) ? data : []);
      } else {
        setError("Failed to load comments");
      }
    } catch {
      setError("Network error — could not load comments");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const deleteComment = async (id: number, snippet: string) => {
    if (!confirm(`Delete this comment by ${snippet}? This cannot be undone.`)) return;
    setDeleting(id);
    setError(null);
    try {
      const res = await fetch(`/api/admin/comments/${id}`, { method: "DELETE" });
      if (res.ok) {
        await load();
      } else {
        const err = await res.json().catch(() => ({})) as { detail?: string };
        setError(err.detail ?? "Failed to delete comment");
      }
    } catch {
      setError("Network error — could not delete comment");
    } finally {
      setDeleting(null);
    }
  };

  const filtered = comments.filter((c) => {
    const q = search.toLowerCase();
    return (
      c.content.toLowerCase().includes(q) ||
      (c.user?.username ?? "").toLowerCase().includes(q)
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
            placeholder="Search comments…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-3 py-2 bg-hover border border-border rounded-lg text-sm text-[#f1f1f5] placeholder:text-muted focus:outline-none focus:border-accent/60 transition-colors"
          />
        </div>
        <span className="text-muted text-xs shrink-0">
          {loading ? "Loading…" : `${filtered.length} of ${comments.length} comment${comments.length !== 1 ? "s" : ""}`}
        </span>
      </div>

      {/* Error banner */}
      {error && (
        <div className="flex items-center gap-2 text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-4 py-3">
          <IconError />
          {error}
          <button
            onClick={() => setError(null)}
            className="ml-auto text-red-400/60 hover:text-red-400 transition-colors"
          >
            ✕
          </button>
        </div>
      )}

      {/* Table */}
      <div className="overflow-x-auto -mx-1">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border text-left">
              <th className="pb-3 pr-4 text-xs font-semibold text-muted uppercase tracking-wider">Comment</th>
              <th className="pb-3 pr-4 text-xs font-semibold text-muted uppercase tracking-wider">Author</th>
              <th className="pb-3 pr-4 text-xs font-semibold text-muted uppercase tracking-wider">Date</th>
              <th className="pb-3 text-xs font-semibold text-muted uppercase tracking-wider text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              Array.from({ length: 4 }).map((_, i) => <SkeletonRow key={i} />)
            ) : filtered.length === 0 ? (
              <tr>
                <td colSpan={4} className="py-16 text-center">
                  <div className="flex flex-col items-center gap-2 text-muted">
                    <svg width="32" height="32" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.2} className="opacity-40">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M7.5 8.25h9m-9 3H12m-9.75 1.51c0 1.6 1.123 2.994 2.707 3.227 1.129.166 2.27.293 3.423.379.35.026.67.21.865.501L12 21l2.755-4.133a1.14 1.14 0 01.865-.501 48.172 48.172 0 003.423-.379c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0012 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018z" />
                    </svg>
                    <p className="text-sm">{search ? "No comments match your search" : "No comments yet"}</p>
                  </div>
                </td>
              </tr>
            ) : (
              filtered.map((c) => {
                const author = c.user?.username ?? "Unknown";
                return (
                  <tr
                    key={c.id}
                    className="border-b border-border/40 hover:bg-hover/50 transition-colors group"
                  >
                    {/* Comment content */}
                    <td className="py-3.5 pr-4 max-w-sm">
                      <div className="flex flex-col gap-0.5">
                        <p className="text-[#f1f1f5] line-clamp-2 leading-relaxed">{c.content}</p>
                        {c.article_id && (
                          <Link
                            href={`/posts/${c.article_id}`}
                            className="inline-flex items-center gap-1 text-xs text-muted hover:text-accent transition-colors w-fit"
                          >
                            <IconExternalLink />
                            Post #{c.article_id}
                          </Link>
                        )}
                      </div>
                    </td>

                    {/* Author */}
                    <td className="py-3.5 pr-4">
                      <div className="flex items-center gap-2">
                        <Avatar name={author} />
                        <span className="text-muted">{author}</span>
                      </div>
                    </td>

                    {/* Date */}
                    <td className="py-3.5 pr-4 text-muted text-xs whitespace-nowrap">
                      {formatDate(c.created_date)}
                    </td>

                    {/* Actions */}
                    <td className="py-3.5 text-right">
                      <button
                        onClick={() => deleteComment(c.id, author)}
                        disabled={deleting === c.id}
                        title="Delete comment"
                        className="inline-flex items-center gap-1.5 text-xs text-muted hover:text-red-400 hover:bg-red-500/10 border border-transparent hover:border-red-500/20 rounded-md px-2.5 py-1.5 transition-all disabled:opacity-40 disabled:cursor-not-allowed"
                      >
                        <IconTrash />
                        {deleting === c.id ? "Deleting…" : "Delete"}
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
