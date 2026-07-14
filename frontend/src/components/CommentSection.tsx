"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";

type Comment = {
  id: number;
  content: string;
  parent_id?: number | null;
  likes_count: number;
  liked_by_me: boolean;
  user?: { username: string; avatar_url?: string | null } | null;
  created_date: string;
  updated_date?: string | null;
};

function Avatar({ user }: { user: Comment["user"] }) {
  return (
    <div className="w-7 h-7 rounded-full bg-accent-soft flex items-center justify-center text-[11px] font-bold text-accent shrink-0 overflow-hidden">
      {user?.avatar_url ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img src={user.avatar_url} alt={user.username} className="w-full h-full object-cover" />
      ) : (
        (user?.username?.[0] ?? "?").toUpperCase()
      )}
    </div>
  );
}

function CommentComposer({
  onSubmit,
  placeholder,
  initial = "",
  submitLabel = "Post",
  onCancel,
}: {
  onSubmit: (text: string) => Promise<boolean>;
  placeholder: string;
  initial?: string;
  submitLabel?: string;
  onCancel?: () => void;
}) {
  const [text, setText] = useState(initial);
  const [busy, setBusy] = useState(false);

  return (
    <div>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder={placeholder}
        rows={3}
        maxLength={2000}
        className="w-full bg-surface border border-border rounded-xl px-4 py-3 text-ink placeholder:text-muted focus:outline-none focus:border-accent transition-colors resize-none mb-2 text-sm"
      />
      <div className="flex gap-2">
        <button
          onClick={async () => {
            if (!text.trim() || busy) return;
            setBusy(true);
            const ok = await onSubmit(text.trim());
            setBusy(false);
            if (ok) setText("");
          }}
          disabled={busy || !text.trim()}
          className="bg-accent hover:bg-accent-hover disabled:opacity-50 text-white px-4 py-1.5 rounded-full transition-colors text-sm font-medium"
        >
          {busy ? "…" : submitLabel}
        </button>
        {onCancel && (
          <button onClick={onCancel} className="text-sm text-muted hover:text-ink px-3 transition-colors">
            Cancel
          </button>
        )}
      </div>
    </div>
  );
}

export default function CommentSection({ articleId }: { articleId: number }) {
  const { user } = useAuth();
  const [comments, setComments] = useState<Comment[]>([]);
  const [replyTo, setReplyTo] = useState<number | null>(null);
  const [editing, setEditing] = useState<number | null>(null);
  const [error, setError] = useState("");

  const load = useCallback(() => {
    fetch(`/api/comments/${articleId}`)
      .then((r) => (r.ok ? r.json() : []))
      .then((data) => setComments(Array.isArray(data) ? data : []))
      .catch(() => {});
  }, [articleId]);

  useEffect(load, [load]);

  const post = async (content: string, parentId?: number): Promise<boolean> => {
    setError("");
    try {
      const res = await fetch("/api/comments/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content, article_id: articleId, parent_id: parentId ?? null }),
      });
      if (!res.ok) {
        setError("Failed to post comment. Please try again.");
        return false;
      }
      const created: Comment = await res.json();
      setComments((c) => [...c, created]);
      setReplyTo(null);
      return true;
    } catch {
      setError("Network error. Please try again.");
      return false;
    }
  };

  const saveEdit = async (id: number, content: string): Promise<boolean> => {
    const res = await fetch(`/api/comments/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content }),
    });
    if (!res.ok) return false;
    const updated: Comment = await res.json();
    setComments((cs) => cs.map((c) => (c.id === id ? { ...c, ...updated } : c)));
    setEditing(null);
    return true;
  };

  const toggleLike = async (c: Comment) => {
    if (!user) return;
    const res = await fetch(`/api/comments/${c.id}/like`, {
      method: c.liked_by_me ? "DELETE" : "POST",
    });
    if (res.ok) {
      const updated: Comment = await res.json();
      setComments((cs) => cs.map((x) => (x.id === c.id ? { ...x, ...updated } : x)));
    }
  };

  const remove = async (id: number) => {
    const res = await fetch(`/api/comments/${id}`, { method: "DELETE" });
    if (res.ok) setComments((cs) => cs.filter((c) => c.id !== id && c.parent_id !== id));
  };

  const topLevel = comments
    .filter((c) => !c.parent_id)
    .sort((a, b) => +new Date(b.created_date) - +new Date(a.created_date));
  const repliesFor = (id: number) =>
    comments
      .filter((c) => c.parent_id === id)
      .sort((a, b) => +new Date(a.created_date) - +new Date(b.created_date));

  const CommentBody = ({ c, isReply = false }: { c: Comment; isReply?: boolean }) => (
    <div className={`${isReply ? "ml-9 mt-3" : ""}`}>
      <div className="bg-surface border border-border rounded-2xl p-4">
        <div className="flex items-center gap-2 mb-2 text-xs text-muted">
          <Avatar user={c.user} />
          <Link href={`/profile/${c.user?.username ?? ""}`} className="font-medium text-ink-soft hover:text-ink transition-colors">
            {c.user?.username ?? "Unknown"}
          </Link>
          <span aria-hidden>·</span>
          <span>{new Date(c.created_date).toLocaleDateString()}</span>
          {c.updated_date && <span className="italic">(edited)</span>}
        </div>

        {editing === c.id ? (
          <CommentComposer
            initial={c.content}
            placeholder="Edit your comment…"
            submitLabel="Save"
            onSubmit={(text) => saveEdit(c.id, text)}
            onCancel={() => setEditing(null)}
          />
        ) : (
          <p className="text-ink text-sm leading-relaxed whitespace-pre-wrap">{c.content}</p>
        )}

        <div className="flex items-center gap-4 mt-3 text-xs text-muted">
          <button
            onClick={() => toggleLike(c)}
            disabled={!user}
            className={`flex items-center gap-1 transition-colors disabled:opacity-50 ${
              c.liked_by_me ? "text-accent" : "hover:text-accent"
            }`}
          >
            <span aria-hidden>{c.liked_by_me ? "♥" : "♡"}</span>
            {c.likes_count > 0 && c.likes_count}
          </button>
          {user && !isReply && (
            <button onClick={() => setReplyTo(replyTo === c.id ? null : c.id)} className="hover:text-ink transition-colors">
              Reply
            </button>
          )}
          {user?.username === c.user?.username && editing !== c.id && (
            <>
              <button onClick={() => setEditing(c.id)} className="hover:text-ink transition-colors">
                Edit
              </button>
              <button onClick={() => remove(c.id)} className="hover:text-red-400 transition-colors">
                Delete
              </button>
            </>
          )}
        </div>
      </div>

      {replyTo === c.id && (
        <div className="ml-9 mt-3">
          <CommentComposer
            placeholder={`Reply to ${c.user?.username ?? "comment"}…`}
            submitLabel="Reply"
            onSubmit={(text) => post(text, c.id)}
            onCancel={() => setReplyTo(null)}
          />
        </div>
      )}

      {repliesFor(c.id).map((r) => (
        <CommentBody key={r.id} c={r} isReply />
      ))}
    </div>
  );

  return (
    <div>
      <h3 className="font-display text-2xl text-ink mb-6">
        Conversation <span className="text-muted text-lg">({comments.length})</span>
      </h3>

      {user ? (
        <div className="mb-8">
          <CommentComposer placeholder="Join the conversation…" onSubmit={(text) => post(text)} />
          {error && <p className="text-red-400 text-sm mt-2">{error}</p>}
        </div>
      ) : (
        <p className="text-muted text-sm mb-8">
          <Link href="/login" className="text-accent hover:underline">Sign in</Link> to join the conversation.
        </p>
      )}

      <div className="space-y-4">
        {topLevel.map((c) => (
          <CommentBody key={c.id} c={c} />
        ))}
        {comments.length === 0 && (
          <p className="text-muted text-sm text-center py-8">No comments yet. Be the first!</p>
        )}
      </div>
    </div>
  );
}
