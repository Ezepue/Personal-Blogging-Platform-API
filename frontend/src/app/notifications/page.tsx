"use client";

import { useEffect } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { useNotificationContext } from "@/contexts/NotificationContext";
import { useRouter } from "next/navigation";

const TYPE_META: Record<string, { icon: string; label: string }> = {
  like: { icon: "♥", label: "Like" },
  comment: { icon: "💬", label: "Comment" },
  follow: { icon: "✚", label: "Follow" },
  mention: { icon: "@", label: "Mention" },
  system: { icon: "✳", label: "System" },
};

export default function NotificationsPage() {
  const { user, loading } = useAuth();
  const { notifications, markRead, markAllRead } = useNotificationContext();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) router.push("/login");
  }, [user, loading, router]);

  if (loading || !user)
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="w-8 h-8 border-2 border-accent border-t-transparent rounded-full animate-spin" />
      </div>
    );

  return (
    <div className="max-w-2xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <h1 className="font-display text-4xl text-ink">
          Notif<span className="display-italic">ications</span>
        </h1>
        {notifications.some((n) => !n.is_read) && (
          <button onClick={markAllRead} className="text-sm text-accent hover:underline">
            Mark all read
          </button>
        )}
      </div>

      <div className="space-y-2">
        {notifications.length === 0 ? (
          <p className="text-muted text-center py-16">All quiet — no notifications yet.</p>
        ) : (
          notifications.map((n) => {
            const meta = TYPE_META[n.type ?? "system"] ?? TYPE_META.system;
            return (
              <div
                key={n.id}
                onClick={() => {
                  markRead(n.id);
                  const articleId = n.extra_data?.article_id;
                  if (typeof articleId === "number" || typeof articleId === "string") {
                    router.push(`/posts/${articleId}`);
                  } else if (typeof n.extra_data?.follower_username === "string") {
                    router.push(`/profile/${n.extra_data.follower_username}`);
                  }
                }}
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
                  <p className="text-xs text-muted mt-1">{new Date(n.created_at).toLocaleString()}</p>
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
