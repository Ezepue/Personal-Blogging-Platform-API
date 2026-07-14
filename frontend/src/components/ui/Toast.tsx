"use client";

import { createContext, useCallback, useContext, useState, ReactNode } from "react";

type ToastKind = "success" | "error" | "info";

type Toast = {
  id: number;
  message: string;
  kind: ToastKind;
  action?: { label: string; onClick: () => void };
};

type ToastApi = {
  toast: (message: string, kind?: ToastKind, action?: Toast["action"]) => void;
};

const ToastContext = createContext<ToastApi | null>(null);

let nextId = 1;

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const remove = useCallback((id: number) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const toast = useCallback(
    (message: string, kind: ToastKind = "info", action?: Toast["action"]) => {
      const id = nextId++;
      setToasts((prev) => [...prev, { id, message, kind, action }]);
      setTimeout(() => remove(id), action ? 6000 : 3500);
    },
    [remove],
  );

  return (
    <ToastContext.Provider value={{ toast }}>
      {children}
      <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-[80] flex flex-col items-center gap-2 w-[calc(100%-2rem)] max-w-sm">
        {toasts.map((t) => (
          <div
            key={t.id}
            role="status"
            className="fade-up w-full flex items-center gap-3 rounded-xl border border-border bg-surface shadow-lift px-4 py-3 text-sm"
          >
            <span
              aria-hidden
              className={`w-1.5 h-1.5 rounded-full shrink-0 ${
                t.kind === "success" ? "bg-green-500" : t.kind === "error" ? "bg-red-500" : "bg-accent"
              }`}
            />
            <span className="flex-1 text-ink">{t.message}</span>
            {t.action && (
              <button
                onClick={() => {
                  t.action!.onClick();
                  remove(t.id);
                }}
                className="text-accent font-medium hover:underline shrink-0"
              >
                {t.action.label}
              </button>
            )}
            <button
              onClick={() => remove(t.id)}
              aria-label="Dismiss"
              className="text-muted hover:text-ink shrink-0"
            >
              ✕
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast(): ToastApi {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast must be used within ToastProvider");
  return ctx;
}
