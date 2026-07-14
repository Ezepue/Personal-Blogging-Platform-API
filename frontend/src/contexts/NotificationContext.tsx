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

function defaultWsBaseUrl(): string {
  if (process.env.NEXT_PUBLIC_WS_URL) return process.env.NEXT_PUBLIC_WS_URL;
  // Derive from the current origin so an HTTPS page uses wss:// (avoids mixed content).
  if (typeof window !== "undefined") {
    const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
    return `${proto}//${window.location.hostname}:8000`;
  }
  return "ws://localhost:8000";
}

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
    let attempts = 0;

    const scheduleReconnect = () => {
      if (cancelled) return;
      // Exponential backoff capped at 30s.
      const delay = Math.min(30000, 1000 * 2 ** attempts);
      attempts += 1;
      reconnectRef.current = setTimeout(connectWs, delay);
    };

    const connectWs = async () => {
      if (cancelled) return;
      let token: string;
      try {
        const tokenRes = await fetch("/api/auth/token-for-ws");
        if (!tokenRes.ok || cancelled) {
          scheduleReconnect();
          return;
        }
        ({ token } = (await tokenRes.json()) as { token: string });
      } catch {
        scheduleReconnect();
        return;
      }
      if (cancelled) return;

      const ws = new WebSocket(`${defaultWsBaseUrl()}/notification/ws/${user.id}?token=${token}`);
      wsRef.current = ws;

      ws.onopen = () => {
        attempts = 0; // reset backoff on a successful connection
      };

      ws.onmessage = (e) => {
        try {
          const notif: Notification = JSON.parse(e.data as string);
          setNotifications((prev) =>
            prev.some((n) => n.id === notif.id) ? prev : [notif, ...prev]
          );
        } catch {
          // ignore malformed messages
        }
      };

      ws.onerror = () => {
        // onclose will fire next and handle reconnection.
        ws.close();
      };

      ws.onclose = () => {
        scheduleReconnect();
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
