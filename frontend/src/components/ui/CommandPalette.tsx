"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { applyTheme } from "@/lib/theme";

type Command = { id: string; label: string; hint?: string; run: () => void };

/** Global ⌘K / Ctrl+K palette: search, navigation, and theme switching. */
export default function CommandPalette() {
  const router = useRouter();
  const { user } = useAuth();
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [active, setActive] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setOpen((o) => !o);
      } else if (e.key === "Escape") {
        setOpen(false);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  useEffect(() => {
    if (open) {
      setQuery("");
      setActive(0);
      setTimeout(() => inputRef.current?.focus(), 30);
    }
  }, [open]);

  const commands = useMemo<Command[]>(() => {
    const go = (path: string) => () => {
      setOpen(false);
      router.push(path);
    };
    const base: Command[] = [
      { id: "home", label: "Go to Home", run: go("/") },
      { id: "topics", label: "Browse topics", run: go("/topics") },
      { id: "search", label: "Search stories & writers", run: go("/search") },
      { id: "theme-light", label: "Theme: Light", run: () => { applyTheme("light"); setOpen(false); } },
      { id: "theme-dark", label: "Theme: Dark", run: () => { applyTheme("dark"); setOpen(false); } },
      { id: "theme-system", label: "Theme: Follow system", run: () => { applyTheme("system"); setOpen(false); } },
    ];
    if (user) {
      base.push(
        { id: "write", label: "Write a story", run: go("/write") },
        { id: "dashboard", label: "Go to Dashboard", run: go("/dashboard") },
        { id: "bookmarks", label: "Reading list", run: go("/bookmarks") },
        { id: "drafts", label: "My drafts", run: go("/drafts") },
        { id: "history", label: "Reading history", run: go("/history") },
        { id: "notifications", label: "Notifications", run: go("/notifications") },
        { id: "profile", label: "My profile", run: go(`/profile/${user.username}`) },
        { id: "settings", label: "Settings", run: go("/settings") },
      );
    }
    return base;
  }, [router, user]);

  const filtered = commands.filter((c) => c.label.toLowerCase().includes(query.toLowerCase()));

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-[95] flex items-start justify-center pt-[15vh] px-4 bg-black/50 backdrop-blur-sm"
      onClick={() => setOpen(false)}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-label="Command palette"
        className="fade-up w-full max-w-lg rounded-2xl border border-border bg-surface shadow-lift overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        <input
          ref={inputRef}
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setActive(0);
          }}
          onKeyDown={(e) => {
            if (e.key === "ArrowDown") { e.preventDefault(); setActive((a) => Math.min(a + 1, filtered.length - 1)); }
            if (e.key === "ArrowUp") { e.preventDefault(); setActive((a) => Math.max(a - 1, 0)); }
            if (e.key === "Enter") { e.preventDefault(); filtered[active]?.run(); }
          }}
          placeholder="Type a command or search…"
          className="w-full bg-transparent px-5 py-4 text-ink placeholder:text-muted outline-none border-b border-border"
        />
        <ul className="max-h-80 overflow-y-auto py-2">
          {filtered.length === 0 && <li className="px-5 py-3 text-sm text-muted">No matching commands</li>}
          {filtered.map((c, i) => (
            <li key={c.id}>
              <button
                onMouseEnter={() => setActive(i)}
                onClick={c.run}
                className={`w-full text-left px-5 py-2.5 text-sm transition-colors ${
                  i === active ? "bg-raised text-ink" : "text-ink-soft"
                }`}
              >
                {c.label}
              </button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
