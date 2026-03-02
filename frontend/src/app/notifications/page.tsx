"use client";

import { useEffect } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { useNotifications } from "@/hooks/useNotifications";
import { useRouter } from "next/navigation";

export default function NotificationsPage() {
  const { user, loading } = useAuth();
  const { notifications, markRead, markAllRead } = useNotifications();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) router.push("/login");
  }, [user, loading, router]);

  if (loading || !user) return null;

  return (
    <div className="max-w-2xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-[#f1f1f5]">Notifications</h1>
        {notifications.some((n) => !n.is_read) && (
          <button
            onClick={markAllRead}
            className="text-sm text-accent hover:underline"
          >
            Mark all read
          </button>
        )}
      </div>

      <div className="space-y-2">
        {notifications.length === 0 ? (
          <p className="text-muted text-center py-16">No notifications yet.</p>
        ) : (
          notifications.map((n) => (
            <div
              key={n.id}
              onClick={() => {
                markRead(n.id);
                if (n.extra_data?.article_id) router.push(`/posts/${n.extra_data.article_id}`);
              }}
              className={`bg-surface border rounded-xl px-5 py-4 cursor-pointer hover:border-accent transition-colors flex items-start gap-3 ${
                !n.is_read ? "border-accent/40" : "border-border"
              }`}
            >
              {!n.is_read && (
                <span className="w-2 h-2 rounded-full bg-accent flex-shrink-0 mt-2" />
              )}
              <div className={!n.is_read ? "" : "ml-5"}>
                <p className="text-[#f1f1f5]">{n.message}</p>
                <p className="text-xs text-muted mt-1">
                  {new Date(n.created_at).toLocaleString()}
                </p>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
