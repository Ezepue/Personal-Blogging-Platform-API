"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/contexts/AuthContext";

type Comment = {
  id: number;
  content: string;
  is_deleted: boolean;
  user: { username: string; avatar_url?: string | null };
  created_date: string;
};

export default function CommentSection({ articleId }: { articleId: number }) {
  const { user } = useAuth();
  const [comments, setComments] = useState<Comment[]>([]);
  const [text, setText] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch(`/api/comments/${articleId}`)
      .then((r) => r.json())
      .then((data) => setComments(Array.isArray(data) ? data.filter((c: Comment) => !c.is_deleted) : []))
      .catch(() => {});
  }, [articleId]);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim()) return;
    setSubmitting(true);
    setError("");
    try {
      const res = await fetch("/api/comments/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: text.trim(), article_id: articleId }),
      });
      if (res.ok) {
        const newComment = await res.json();
        setComments((c) => [newComment, ...c]);
        setText("");
      } else {
        setError("Failed to post comment. Please try again.");
      }
    } catch {
      setError("Network error. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div>
      <h3 className="text-xl font-bold text-[#f1f1f5] mb-6">
        Comments ({comments.length})
      </h3>

      {user ? (
        <form onSubmit={submit} className="mb-8">
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Write a comment..."
            rows={3}
            maxLength={2000}
            className="w-full bg-surface border border-border rounded-lg px-4 py-3 text-[#f1f1f5] placeholder:text-muted focus:outline-none focus:border-accent transition-colors resize-none mb-2"
          />
          {error && <p className="text-red-400 text-sm mb-2">{error}</p>}
          <button
            type="submit"
            disabled={submitting || !text.trim()}
            className="bg-accent hover:bg-accent-hover disabled:opacity-50 text-white px-4 py-2 rounded-lg transition-colors text-sm font-medium"
          >
            {submitting ? "Posting…" : "Post comment"}
          </button>
        </form>
      ) : (
        <p className="text-muted text-sm mb-8">
          <a href="/login" className="text-accent hover:underline">Sign in</a> to leave a comment.
        </p>
      )}

      <div className="space-y-4">
        {comments.map((c) => (
          <div
            key={c.id}
            className="bg-surface border border-border rounded-xl p-4"
          >
            <div className="flex items-center gap-2 mb-2 text-sm text-muted">
              <div className="w-5 h-5 rounded-full bg-accent/20 flex items-center justify-center text-xs font-bold text-accent flex-shrink-0 overflow-hidden">
                {c.user?.avatar_url ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img src={c.user.avatar_url} alt={c.user?.username} className="w-full h-full object-cover" />
                ) : (
                  c.user?.username?.[0]?.toUpperCase() ?? "?"
                )}
              </div>
              <span>{c.user?.username ?? "Unknown"}</span>
              <span aria-hidden>·</span>
              <span>{new Date(c.created_date).toLocaleDateString()}</span>
            </div>
            <p className="text-[#f1f1f5] text-sm leading-relaxed whitespace-pre-wrap">
              {c.content}
            </p>
          </div>
        ))}
        {comments.length === 0 && (
          <p className="text-muted text-sm text-center py-8">
            No comments yet. Be the first!
          </p>
        )}
      </div>
    </div>
  );
}
