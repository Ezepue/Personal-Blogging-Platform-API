"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { useAuth } from "@/contexts/AuthContext";

type Notification = {
  id: number;
  message: string;
  is_read: boolean;
  created_at: string;
  extra_data?: Record<string, unknown>;
};

export function useNotifications() {
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
    if (!user) return;
    fetchNotifications();

    const connectWs = async () => {
      const tokenRes = await fetch("/api/auth/token-for-ws");
      if (!tokenRes.ok) return;
      const { token } = await tokenRes.json();

      const wsBaseUrl = process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000";
      const ws = new WebSocket(`${wsBaseUrl}/notification/ws/${user.id}?token=${token}`);
      wsRef.current = ws;

      ws.onmessage = (e) => {
        try {
          const notif: Notification = JSON.parse(e.data);
          setNotifications((prev) => [notif, ...prev]);
        } catch {
          // ignore malformed messages
        }
      };

      ws.onclose = () => {
        // Reconnect after 5s on unexpected close
        reconnectRef.current = setTimeout(connectWs, 5000);
      };
    };

    connectWs();

    return () => {
      if (reconnectRef.current) clearTimeout(reconnectRef.current);
      wsRef.current?.close();
    };
  }, [user, fetchNotifications]);

  const markRead = async (id: number) => {
    await fetch(`/api/notification/read/${id}`, { method: "POST" });
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
    );
  };

  const markAllRead = async () => {
    await fetch("/api/notification/read-all", { method: "POST" });
    setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
  };

  return {
    notifications,
    unreadCount: notifications.filter((n) => !n.is_read).length,
    markRead,
    markAllRead,
    refresh: fetchNotifications,
  };
}
