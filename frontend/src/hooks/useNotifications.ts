"use client";
// This hook is a thin wrapper around the shared NotificationContext.
// Always use NotificationProvider in the layout to share a single WebSocket connection.
export { useNotificationContext as useNotifications } from "@/contexts/NotificationContext";
