"use client";

import { useCallback, useEffect, useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { useNotificationContext } from "@/contexts/NotificationContext";
import { useRouter } from "next/navigation";
import { timeAgo, formatDateTime } from "@/lib/format";
import { api } from "@/lib/api";

const TYPE_META: Record<string, { icon: string; label: string }> = {
  like: { icon: "♥", label: "Like" },
  comment: { icon: "💬", label: "Comment" },
  follow: { icon: "✚", label: "Follow" },
  mention: { icon: "@", label: "Mention" },
  system: { icon: "✳", label: "System" },
};

type Note = {
  id: number;
  message: string;
  type?: string;
  is_read: boolean;
  created_at: string;
  extra_data?: Record<string, unknown>;
};

export default function NotificationsPage() {
  const { user, loading } = useAuth();
  const { markRead, markAllRead, refresh } = useNotificationContext();
  const router = useRouter();
  const [notes, setNotes] = useState<Note[]>([]);
  const [filter, setFilter] = useState<"all" | "unread">("all");
  const [fetching, setFetching] = useState(true);

  useEffect(() => {
    if (!loading && !user) router.push("/login");
  }, [user, loading, router]);

  // The bell holds only unread; this page shows the full history.
  const load = useCallback(() => {
    if (!user) return;
    api.get<Note[]>("/notification/?limit=100")
      .then((data) => setNotes(Array.isArray(data) ? data : []))
      .catch(() => {})
      .finally(() => setFetching(false));
  }, [user]);

  useEffect(load, [load]);

  const open = (n: Note) => {
    if (!n.is_read) {
      markRead(n.id); // keep the bell's unread count in sync
      setNotes((prev) => prev.map((x) => (x.id === n.id ? { ...x, is_read: true } : x)));
    }
    const articleId = n.extra_data?.article_id;
    if (typeof articleId === "number" || typeof articleId === "string") {
      router.push(`/posts/${articleId}`);
    } else if (typeof n.extra_data?.follower_username === "string") {
      router.push(`/profile/${n.extra_data.follower_username}`);
    }
  };

  const markAll = async () => {
    await markAllRead();
    setNotes((prev) => prev.map((n) => ({ ...n, is_read: true })));
    refresh();
  };

  if (loading || !user)
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="w-8 h-8 border-2 border-accent border-t-transparent rounded-full animate-spin" />
      </div>
    );

  const visible = filter === "unread" ? notes.filter((n) => !n.is_read) : notes;

  return (
    <div className="max-w-2xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <h1 className="font-display text-4xl text-ink">
          Notif<span className="display-italic">ications</span>
        </h1>
        {notes.some((n) => !n.is_read) && (
          <button onClick={markAll} className="text-sm text-accent hover:underline">
            Mark all read
          </button>
        )}
      </div>

      <div className="flex items-center gap-1 border border-border rounded-full p-0.5 text-xs w-fit mb-6">
        {(["all", "unread"] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-4 py-1.5 rounded-full capitalize transition-colors ${
              filter === f ? "bg-accent text-white" : "text-muted hover:text-ink"
            }`}
          >
            {f}
          </button>
        ))}
      </div>

      <div className="space-y-2">
        {fetching ? (
          <div className="flex justify-center py-16">
            <div className="w-6 h-6 border-2 border-accent border-t-transparent rounded-full animate-spin" />
          </div>
        ) : visible.length === 0 ? (
          <p className="text-muted text-center py-16">
            {filter === "unread" ? "You’re all caught up." : "All quiet — no notifications yet."}
          </p>
        ) : (
          visible.map((n) => {
            const meta = TYPE_META[n.type ?? "system"] ?? TYPE_META.system;
            return (
              <div
                key={n.id}
                onClick={() => open(n)}
                className={`bg-surface border rounded-2xl px-5 py-4 cursor-pointer hover:border-accent transition-colors flex items-start gap-4 shadow-soft ${
                  !n.is_read ? "border-accent" : "border-border"
                }`}
              >
                <span
                  aria-label={meta.label}
                  title={meta.label}
                  className="w-9 h-9 rounded-full bg-accent-soft text-accent flex items-center justify-center text-sm shrink-0"
                >
                  {meta.icon}
                </span>
                <div className="min-w-0 flex-1">
                  <p className={`${n.is_read ? "text-ink-soft" : "text-ink"} leading-relaxed`}>{n.message}</p>
                  <p className="text-xs text-muted mt-1" title={formatDateTime(n.created_at)}>{timeAgo(n.created_at)}</p>
                </div>
                {!n.is_read && <span className="w-2 h-2 rounded-full bg-accent shrink-0 mt-2" aria-label="Unread" />}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
