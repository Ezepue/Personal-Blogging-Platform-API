"use client";

import { createContext, useCallback, useContext, useEffect, useRef, useState, ReactNode } from "react";

type ConfirmOptions = {
  title: string;
  message?: string;
  confirmLabel?: string;
  cancelLabel?: string;
  destructive?: boolean;
};

type ConfirmApi = { confirm: (options: ConfirmOptions) => Promise<boolean> };

const ConfirmContext = createContext<ConfirmApi | null>(null);

export function ConfirmProvider({ children }: { children: ReactNode }) {
  const [options, setOptions] = useState<ConfirmOptions | null>(null);
  const resolver = useRef<((v: boolean) => void) | null>(null);

  const confirm = useCallback((opts: ConfirmOptions) => {
    setOptions(opts);
    return new Promise<boolean>((resolve) => {
      resolver.current = resolve;
    });
  }, []);

  const settle = useCallback((value: boolean) => {
    resolver.current?.(value);
    resolver.current = null;
    setOptions(null);
  }, []);

  useEffect(() => {
    if (!options) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") settle(false);
      if (e.key === "Enter") settle(true);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [options, settle]);

  return (
    <ConfirmContext.Provider value={{ confirm }}>
      {children}
      {options && (
        <div
          className="fixed inset-0 z-[90] flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
          onClick={() => settle(false)}
        >
          <div
            role="alertdialog"
            aria-modal="true"
            className="fade-up w-full max-w-sm rounded-2xl border border-border bg-surface shadow-lift p-6"
            onClick={(e) => e.stopPropagation()}
          >
            <h2 className="font-display text-xl text-ink mb-2">{options.title}</h2>
            {options.message && <p className="text-muted text-sm leading-relaxed mb-6">{options.message}</p>}
            <div className="flex justify-end gap-3">
              <button
                onClick={() => settle(false)}
                className="px-4 py-2 rounded-full text-sm text-muted hover:text-ink border border-border hover:border-ink transition-colors"
              >
                {options.cancelLabel ?? "Cancel"}
              </button>
              <button
                autoFocus
                onClick={() => settle(true)}
                className={`px-4 py-2 rounded-full text-sm font-medium text-white transition-colors ${
                  options.destructive ? "bg-red-600 hover:bg-red-700" : "bg-accent hover:bg-accent-hover"
                }`}
              >
                {options.confirmLabel ?? "Confirm"}
              </button>
            </div>
          </div>
        </div>
      )}
    </ConfirmContext.Provider>
  );
}

export function useConfirm(): ConfirmApi {
  const ctx = useContext(ConfirmContext);
  if (!ctx) throw new Error("useConfirm must be used within ConfirmProvider");
  return ctx;
}
