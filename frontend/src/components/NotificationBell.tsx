"use client";

import { useState, useRef, useEffect } from "react";
import { useNotificationContext } from "@/contexts/NotificationContext";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";

export default function NotificationBell() {
  const { user } = useAuth();
  const { notifications, unreadCount, markRead, markAllRead } = useNotificationContext();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const router = useRouter();

  // Close on outside click
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  // Don't render bell for unauthenticated users
  if (!user) return null;

  const handleClick = (n: (typeof notifications)[number]) => {
    markRead(n.id);
    setOpen(false);
    const articleId = n.extra_data?.article_id;
    if (typeof articleId === "number" || typeof articleId === "string") {
      router.push(`/posts/${articleId}`);
    }
  };

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setOpen((o) => !o)}
        className="relative text-muted hover:text-[#f1f1f5] transition-colors"
        aria-label="Notifications"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
          />
        </svg>
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-accent text-white text-[10px] font-bold w-4 h-4 rounded-full flex items-center justify-center">
            {unreadCount > 9 ? "9+" : unreadCount}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 top-8 w-80 bg-surface border border-border rounded-xl shadow-xl z-50 overflow-hidden">
          <div className="flex items-center justify-between px-4 py-3 border-b border-border">
            <span className="font-semibold text-[#f1f1f5] text-sm">Notifications</span>
            <div className="flex items-center gap-3">
              {unreadCount > 0 && (
                <button
                  onClick={markAllRead}
                  className="text-xs text-accent hover:underline"
                >
                  Mark all read
                </button>
              )}
              <button
                onClick={() => { setOpen(false); router.push("/notifications"); }}
                className="text-xs text-muted hover:text-[#f1f1f5]"
              >
                See all
              </button>
            </div>
          </div>

          <div className="max-h-80 overflow-y-auto">
            {notifications.length === 0 ? (
              <p className="text-muted text-sm text-center py-8">No notifications</p>
            ) : (
              notifications.slice(0, 10).map((n) => (
                <button
                  key={n.id}
                  onClick={() => handleClick(n)}
                  className={`w-full text-left px-4 py-3 hover:bg-hover transition-colors border-b border-border/50 last:border-0 ${
                    !n.is_read ? "bg-accent/5" : ""
                  }`}
                >
                  <div className="flex items-start gap-2">
                    {!n.is_read && (
                      <span className="w-2 h-2 rounded-full bg-accent flex-shrink-0 mt-1.5" />
                    )}
                    <div className={!n.is_read ? "" : "ml-4"}>
                      <p className="text-sm text-[#f1f1f5] leading-relaxed">{n.message}</p>
                      <p className="text-xs text-muted mt-0.5">
                        {new Date(n.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                </button>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
