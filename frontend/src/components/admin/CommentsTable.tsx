"use client";

import { useEffect, useState, useCallback } from "react";

type Comment = {
  id: number;
  content: string;
  created_date: string;
  user?: { username: string };
  article_id?: number;
};

export default function CommentsTable() {
  const [comments, setComments] = useState<Comment[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState<number | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/admin/comments");
      if (res.ok) {
        const data = await res.json();
        setComments(Array.isArray(data) ? data : []);
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const deleteComment = async (id: number) => {
    if (!confirm("Delete this comment?")) return;
    setDeleting(id);
    try {
      const res = await fetch(`/api/admin/comments/${id}`, { method: "DELETE" });
      if (res.ok) await load();
    } finally {
      setDeleting(null);
    }
  };

  if (loading) return (
    <div className="flex justify-center py-12">
      <div className="w-6 h-6 border-2 border-accent border-t-transparent rounded-full animate-spin" />
    </div>
  );

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border text-left text-muted">
            <th className="py-3 pr-4 font-medium">Content</th>
            <th className="py-3 pr-4 font-medium">Author</th>
            <th className="py-3 pr-4 font-medium">Date</th>
            <th className="py-3 font-medium"></th>
          </tr>
        </thead>
        <tbody>
          {comments.length === 0 ? (
            <tr>
              <td colSpan={4} className="py-12 text-center text-muted">No comments found</td>
            </tr>
          ) : (
            comments.map((c) => (
              <tr key={c.id} className="border-b border-border/50 hover:bg-hover transition-colors">
                <td className="py-3 pr-4 text-[#f1f1f5] max-w-xs">
                  <span className="truncate block">{c.content}</span>
                </td>
                <td className="py-3 pr-4 text-muted">{c.user?.username ?? "—"}</td>
                <td className="py-3 pr-4 text-muted text-xs">
                  {new Date(c.created_date).toLocaleDateString()}
                </td>
                <td className="py-3">
                  <button
                    onClick={() => deleteComment(c.id)}
                    disabled={deleting === c.id}
                    className="text-red-400 hover:text-red-300 text-xs transition-colors disabled:opacity-50"
                  >
                    {deleting === c.id ? "Deleting…" : "Delete"}
                  </button>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
