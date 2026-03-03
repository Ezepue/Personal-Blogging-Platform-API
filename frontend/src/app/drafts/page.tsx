"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";

type Draft = {
  id: number;
  title: string;
  content: string;
  category?: string | null;
  tags: string[];
  updated_date?: string | null;
};

function excerpt(content: string, max = 80): string {
  const plain = content.replace(/<[^>]+>/g, "");
  return plain.length > max ? plain.slice(0, max) + "…" : plain;
}

function formatDate(iso: string | null | undefined): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export default function DraftsPage() {
  const { user, loading } = useAuth();
  const router = useRouter();

  const [drafts, setDrafts] = useState<Draft[]>([]);
  const [fetching, setFetching] = useState(true);
  const [publishing, setPublishing] = useState<number | null>(null);
  const [deleting, setDeleting] = useState<number | null>(null);
  const [error, setError] = useState("");

  const fetchDrafts = useCallback(() => {
    setFetching(true);
    fetch("/api/articles/my-drafts")
      .then((r) => (r.ok ? r.json() : []))
      .then(setDrafts)
      .catch(() => setDrafts([]))
      .finally(() => setFetching(false));
  }, []);

  useEffect(() => {
    if (loading) return;
    if (!user) { router.push("/login"); return; }
    if (user.role === "READER") { router.push("/"); return; }
    fetchDrafts();
  }, [user, loading, router, fetchDrafts]);

  const publishDraft = async (id: number) => {
    setPublishing(id);
    setError("");
    try {
      const res = await fetch(`/api/articles/${id}/publish`, { method: "PUT" });
      if (res.ok) {
        setDrafts((prev) => prev.filter((d) => d.id !== id));
        // Invalidate any cached server-component pages (home, profile) so
        // the newly published post appears immediately without a manual reload.
        router.refresh();
      } else {
        const err = await res.json().catch(() => ({}));
        setError((err as { detail?: string }).detail ?? "Failed to publish");
      }
    } finally {
      setPublishing(null);
    }
  };

  const deleteDraft = async (id: number, title: string) => {
    if (!confirm(`Delete "${title}"? This cannot be undone.`)) return;
    setDeleting(id);
    setError("");
    try {
      const res = await fetch(`/api/articles/${id}`, { method: "DELETE" });
      if (res.ok) {
        setDrafts((prev) => prev.filter((d) => d.id !== id));
      } else {
        const err = await res.json().catch(() => ({}));
        setError((err as { detail?: string }).detail ?? "Failed to delete");
      }
    } finally {
      setDeleting(null);
    }
  };

  if (loading || !user || user.role === "READER") return null;

  return (
    <div className="max-w-3xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-[#f1f1f5]">My Drafts</h1>
          <p className="text-muted text-sm mt-1">
            {drafts.length} {drafts.length === 1 ? "draft" : "drafts"}
          </p>
        </div>
        <Link
          href="/write"
          className="bg-accent hover:bg-accent-hover text-white px-4 py-2 rounded-lg font-medium text-sm transition-colors"
        >
          + New Post
        </Link>
      </div>

      {error && (
        <p className="text-red-400 text-sm mb-4 bg-red-900/20 border border-red-900/30 rounded-lg px-4 py-2">
          {error}
        </p>
      )}

      {/* Content */}
      {fetching ? (
        <div className="flex items-center justify-center py-20">
          <div className="w-8 h-8 border-2 border-accent border-t-transparent rounded-full animate-spin" />
        </div>
      ) : drafts.length === 0 ? (
        <div className="text-center py-20 border border-dashed border-border rounded-xl">
          <p className="text-muted text-lg mb-4">No drafts yet.</p>
          <Link
            href="/write"
            className="text-accent hover:underline text-sm"
          >
            Start writing →
          </Link>
        </div>
      ) : (
        <div className="grid gap-3">
          {drafts.map((draft) => (
            <article
              key={draft.id}
              className="bg-surface border border-border rounded-xl p-5 hover:border-accent/50 transition-colors"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0 flex-1">
                  <h2 className="font-semibold text-[#f1f1f5] truncate text-lg">
                    {draft.title}
                  </h2>
                  <p className="text-muted text-sm mt-1 line-clamp-2 leading-relaxed">
                    {excerpt(draft.content, 140)}
                  </p>
                  <div className="flex items-center gap-3 mt-2 text-xs text-muted">
                    {draft.category && (
                      <span className="bg-border/50 px-2 py-0.5 rounded-full">
                        {draft.category}
                      </span>
                    )}
                    <span>Edited {formatDate(draft.updated_date)}</span>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2 flex-shrink-0">
                  <Link
                    href={`/write/${draft.id}`}
                    className="px-3 py-1.5 text-xs border border-border rounded-lg text-muted hover:text-[#f1f1f5] hover:border-[#f1f1f5] transition-colors"
                  >
                    Edit
                  </Link>
                  <button
                    onClick={() => publishDraft(draft.id)}
                    disabled={publishing === draft.id}
                    className="px-3 py-1.5 text-xs bg-accent hover:bg-accent-hover text-white rounded-lg transition-colors disabled:opacity-50"
                  >
                    {publishing === draft.id ? "Publishing…" : "Publish"}
                  </button>
                  <button
                    onClick={() => deleteDraft(draft.id, draft.title)}
                    disabled={deleting === draft.id}
                    className="px-3 py-1.5 text-xs border border-red-900/50 text-red-400 hover:bg-red-900/20 rounded-lg transition-colors disabled:opacity-50"
                  >
                    {deleting === draft.id ? "…" : "Delete"}
                  </button>
                </div>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
