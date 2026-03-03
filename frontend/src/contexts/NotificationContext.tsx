"use client";

import { createContext, useContext, useEffect, useRef, useState, useCallback, ReactNode } from "react";
import { useAuth } from "@/contexts/AuthContext";

type Notification = {
  id: number;
  message: string;
  is_read: boolean;
  created_at: string;
  extra_data?: Record<string, unknown>;
};

type NotificationContextValue = {
  notifications: Notification[];
  unreadCount: number;
  markRead: (id: number) => Promise<void>;
  markAllRead: () => Promise<void>;
  refresh: () => Promise<void>;
};

const NotificationContext = createContext<NotificationContextValue | null>(null);

export function NotificationProvider({ children }: { children: ReactNode }) {
  const { user } = useAuth();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const fetchNotifications = useCallback(async () => {
    const res = await fetch("/api/notification/unread");
    if (res.ok) {
      const data = await res.json();
      setNotifications(Array.isArray(data) ? data : []);
    }
  }, []);

  useEffect(() => {
    if (!user) {
      setNotifications([]);
      return;
    }
    fetchNotifications();

    let cancelled = false;

    const connectWs = async () => {
      const tokenRes = await fetch("/api/auth/token-for-ws");
      if (!tokenRes.ok || cancelled) return;
      const { token } = (await tokenRes.json()) as { token: string };
      if (cancelled) return;

      const wsBaseUrl = process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000";
      const ws = new WebSocket(`${wsBaseUrl}/notification/ws/${user.id}?token=${token}`);
      wsRef.current = ws;

      ws.onmessage = (e) => {
        try {
          const notif: Notification = JSON.parse(e.data as string);
          setNotifications((prev) => [notif, ...prev]);
        } catch {
          // ignore malformed messages
        }
      };

      ws.onclose = () => {
        if (cancelled) return;
        reconnectRef.current = setTimeout(connectWs, 5000);
      };
    };

    connectWs();

    return () => {
      cancelled = true;
      if (reconnectRef.current) clearTimeout(reconnectRef.current);
      wsRef.current?.close();
      wsRef.current = null;
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps -- user?.id is intentional: avoids reconnect on object reference change
  }, [user?.id, fetchNotifications]);

  const markRead = async (id: number) => {
    const res = await fetch(`/api/notification/read/${id}`, { method: "POST" });
    if (res.ok) {
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      );
    }
  };

  const markAllRead = async () => {
    const res = await fetch("/api/notification/read-all", { method: "POST" });
    if (res.ok) {
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
    }
  };

  return (
    <NotificationContext.Provider
      value={{
        notifications,
        unreadCount: notifications.filter((n) => !n.is_read).length,
        markRead,
        markAllRead,
        refresh: fetchNotifications,
      }}
    >
      {children}
    </NotificationContext.Provider>
  );
}

export function useNotificationContext(): NotificationContextValue {
  const ctx = useContext(NotificationContext);
  if (!ctx) throw new Error("useNotificationContext must be used within NotificationProvider");
  return ctx;
}
