"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";
import { useToast } from "@/components/ui/Toast";
import { useConfirm } from "@/components/ui/ConfirmDialog";
import { timeAgo, formatDateTime, avatarColor } from "@/lib/format";
import { api } from "@/lib/api";

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

const MAX = 2000;

function Avatar({ user }: { user: Comment["user"] }) {
  const name = user?.username ?? "?";
  return (
    <div
      className="w-7 h-7 rounded-full flex items-center justify-center text-[11px] font-bold text-white shrink-0 overflow-hidden"
      style={user?.avatar_url ? undefined : { backgroundColor: avatarColor(name) }}
    >
      {user?.avatar_url ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img src={user.avatar_url} alt={name} className="w-full h-full object-cover" />
      ) : (
        name[0]?.toUpperCase()
      )}
    </div>
  );
}

function Composer({
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

  const submit = async () => {
    if (!text.trim() || busy) return;
    setBusy(true);
    const ok = await onSubmit(text.trim());
    setBusy(false);
    if (ok) setText("");
  };

  return (
    <div>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => { if ((e.metaKey || e.ctrlKey) && e.key === "Enter") submit(); }}
        placeholder={placeholder}
        rows={3}
        maxLength={MAX}
        className="w-full bg-surface border border-border rounded-xl px-4 py-3 text-ink placeholder:text-muted focus:outline-none focus:border-accent transition-colors resize-none mb-2 text-sm"
      />
      <div className="flex items-center gap-3">
        <button
          onClick={submit}
          disabled={busy || !text.trim()}
          className="bg-accent hover:bg-accent-hover disabled:opacity-50 text-white px-4 py-1.5 rounded-full transition-colors text-sm font-medium"
        >
          {busy ? "…" : submitLabel}
        </button>
        {onCancel && <button onClick={onCancel} className="text-sm text-muted hover:text-ink px-2 transition-colors">Cancel</button>}
        <span className="ml-auto text-xs text-muted tabular-nums">
          <kbd className="font-sans">⌘</kbd>+Enter{text.length > MAX - 200 ? ` · ${MAX - text.length} left` : ""}
        </span>
      </div>
    </div>
  );
}

export default function CommentSection({ articleId }: { articleId: number }) {
  const { user } = useAuth();
  const { toast } = useToast();
  const { confirm } = useConfirm();
  const [comments, setComments] = useState<Comment[]>([]);
  const [replyTo, setReplyTo] = useState<number | null>(null);
  const [editing, setEditing] = useState<number | null>(null);
  const [collapsed, setCollapsed] = useState<Set<number>>(new Set());
  const [sort, setSort] = useState<"new" | "top">("new");

  const load = useCallback(() => {
    api.get<Comment[]>(`/comments/${articleId}?sort=${sort}`)
      .then((data) => setComments(Array.isArray(data) ? data : []))
      .catch(() => {});
  }, [articleId, sort]);

  useEffect(load, [load]);

  const post = async (content: string, parentId?: number): Promise<boolean> => {
    try {
      const created = await api.post<Comment>("/comments/", {
        content, article_id: articleId, parent_id: parentId ?? null,
      });
      setComments((c) => [...c, created]);
      setReplyTo(null);
      toast(parentId ? "Reply posted" : "Comment posted", "success");
      return true;
    } catch {
      toast("Couldn't post your comment", "error");
      return false;
    }
  };

  const saveEdit = async (id: number, content: string): Promise<boolean> => {
    try {
      const updated = await api.put<Comment>(`/comments/${id}`, { content });
      setComments((cs) => cs.map((c) => (c.id === id ? { ...c, ...updated } : c)));
      setEditing(null);
      toast("Comment updated", "success");
      return true;
    } catch {
      toast("Couldn't update comment", "error");
      return false;
    }
  };

  const toggleLike = async (c: Comment) => {
    if (!user) return;
    try {
      const updated = await api[c.liked_by_me ? "del" : "post"]<Comment>(`/comments/${c.id}/like`);
      setComments((cs) => cs.map((x) => (x.id === c.id ? { ...x, ...updated } : x)));
    } catch {
      /* ignore */
    }
  };

  const remove = async (id: number) => {
    if (!(await confirm({ title: "Delete this comment?", confirmLabel: "Delete", destructive: true }))) return;
    try {
      await api.del(`/comments/${id}`);
      setComments((cs) => cs.filter((c) => c.id !== id && c.parent_id !== id));
      toast("Comment deleted", "success");
    } catch {
      toast("Couldn't delete comment", "error");
    }
  };

  const toggleCollapse = (id: number) =>
    setCollapsed((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });

  const topLevel = comments.filter((c) => !c.parent_id);
  const repliesFor = (id: number) =>
    comments.filter((c) => c.parent_id === id).sort((a, b) => +new Date(a.created_date) - +new Date(b.created_date));

  // Rendered as a plain function call (not <Body/>), so it does not create a new
  // component identity each render — the in-progress reply/edit Composer keeps its
  // state when an unrelated comment is liked or the sort changes.
  const renderComment = (c: Comment, isReply = false) => {
    const replies = repliesFor(c.id);
    const isCollapsed = collapsed.has(c.id);
    return (
      <div key={c.id} className={isReply ? "ml-9 mt-3" : ""}>
        <div className="bg-surface border border-border rounded-2xl p-4">
          <div className="flex items-center gap-2 mb-2 text-xs text-muted">
            <Avatar user={c.user} />
            <Link href={`/profile/${c.user?.username ?? ""}`} className="font-medium text-ink-soft hover:text-ink transition-colors">
              {c.user?.username ?? "Unknown"}
            </Link>
            <span aria-hidden>·</span>
            <span title={formatDateTime(c.created_date)}>{timeAgo(c.created_date)}</span>
            {c.updated_date && <span className="italic">(edited)</span>}
          </div>

          {editing === c.id ? (
            <Composer initial={c.content} placeholder="Edit your comment…" submitLabel="Save" onSubmit={(t) => saveEdit(c.id, t)} onCancel={() => setEditing(null)} />
          ) : (
            <p className="text-ink text-sm leading-relaxed whitespace-pre-wrap">{c.content}</p>
          )}

          <div className="flex items-center gap-4 mt-3 text-xs text-muted">
            <button onClick={() => toggleLike(c)} disabled={!user} className={`flex items-center gap-1 transition-colors disabled:opacity-50 ${c.liked_by_me ? "text-accent" : "hover:text-accent"}`}>
              <span aria-hidden>{c.liked_by_me ? "♥" : "♡"}</span>{c.likes_count > 0 && c.likes_count}
            </button>
            {user && !isReply && <button onClick={() => setReplyTo(replyTo === c.id ? null : c.id)} className="hover:text-ink transition-colors">Reply</button>}
            {user?.username === c.user?.username && editing !== c.id && (
              <>
                <button onClick={() => setEditing(c.id)} className="hover:text-ink transition-colors">Edit</button>
                <button onClick={() => remove(c.id)} className="hover:text-red-500 transition-colors">Delete</button>
              </>
            )}
          </div>
        </div>

        {replyTo === c.id && (
          <div className="ml-9 mt-3">
            <Composer placeholder={`Reply to ${c.user?.username ?? "comment"}…`} submitLabel="Reply" onSubmit={(t) => post(t, c.id)} onCancel={() => setReplyTo(null)} />
          </div>
        )}

        {replies.length > 0 && (
          <>
            {replies.length > 2 && (
              <button onClick={() => toggleCollapse(c.id)} className="ml-9 mt-3 text-xs text-accent hover:underline">
                {isCollapsed ? `Show ${replies.length} replies` : "Hide replies"}
              </button>
            )}
            {!isCollapsed && replies.map((r) => renderComment(r, true))}
          </>
        )}
      </div>
    );
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h3 className="font-display text-2xl text-ink">
          Conversation <span className="text-muted text-lg">({comments.length})</span>
        </h3>
        {comments.length > 1 && (
          <div className="flex items-center gap-1 border border-border rounded-full p-0.5 text-xs">
            {(["new", "top"] as const).map((s) => (
              <button
                key={s}
                onClick={() => setSort(s)}
                className={`px-3 py-1 rounded-full transition-colors ${sort === s ? "bg-accent text-white" : "text-muted hover:text-ink"}`}
              >
                {s === "new" ? "Newest" : "Top"}
              </button>
            ))}
          </div>
        )}
      </div>

      {user ? (
        <div className="mb-8"><Composer placeholder="Join the conversation…" onSubmit={(t) => post(t)} /></div>
      ) : (
        <p className="text-muted text-sm mb-8">
          <Link href="/login" className="text-accent hover:underline">Sign in</Link> to join the conversation.
        </p>
      )}

      <div className="space-y-4">
        {topLevel.map((c) => renderComment(c))}
        {comments.length === 0 && <p className="text-muted text-sm text-center py-8">No comments yet. Be the first!</p>}
      </div>
    </div>
  );
}
