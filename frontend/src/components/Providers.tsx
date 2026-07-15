"use client";

import { ReactNode, useEffect } from "react";
import { AuthProvider } from "@/contexts/AuthContext";
import { NotificationProvider } from "@/contexts/NotificationContext";
import { ToastProvider } from "@/components/ui/Toast";
import { ConfirmProvider } from "@/components/ui/ConfirmDialog";
import CommandPalette from "@/components/ui/CommandPalette";

/** Client provider stack shared by every page, plus global system listeners. */
export default function Providers({ children }: { children: ReactNode }) {
  // Keep "follow system" themes in sync when the OS scheme flips at runtime.
  useEffect(() => {
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    const onChange = () => {
      if (!localStorage.getItem("quill-theme")) {
        document.documentElement.setAttribute("data-theme", mq.matches ? "dark" : "light");
      }
    };
    mq.addEventListener("change", onChange);
    return () => mq.removeEventListener("change", onChange);
  }, []);

  return (
    <AuthProvider>
      <NotificationProvider>
        <ToastProvider>
          <ConfirmProvider>
            {children}
            <CommandPalette />
          </ConfirmProvider>
        </ToastProvider>
      </NotificationProvider>
    </AuthProvider>
  );
}
