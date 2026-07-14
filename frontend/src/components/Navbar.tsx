"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import NotificationBell from "./NotificationBell";
import ThemeToggle from "./ThemeToggle";

function Avatar({ username, avatarUrl }: { username: string; avatarUrl?: string | null }) {
  return (
    <div className="w-8 h-8 rounded-full bg-accent-soft border border-border flex items-center justify-center text-xs font-bold text-accent overflow-hidden">
      {avatarUrl ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img src={avatarUrl} alt={username} className="w-full h-full object-cover" />
      ) : (
        username[0]?.toUpperCase()
      )}
    </div>
  );
}

export default function Navbar() {
  const { user, logout, loading } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const close = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) setMenuOpen(false);
    };
    document.addEventListener("mousedown", close);
    return () => document.removeEventListener("mousedown", close);
  }, []);

  const isAdmin = user && (user.role === "ADMIN" || user.role === "SUPER_ADMIN");

  return (
    <nav
      className="sticky top-0 z-50 border-b border-border backdrop-blur-md"
      style={{ backgroundColor: "color-mix(in srgb, var(--surface) 85%, transparent)" }}
    >
      <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between gap-4">
        {/* Wordmark */}
        <Link href="/" className="font-display text-2xl text-ink tracking-tight shrink-0">
          Quill<span className="text-accent">.</span>
        </Link>

        {/* Primary nav */}
        <div className="hidden md:flex items-center gap-6 text-sm text-muted">
          <Link href="/topics" className="link-flourish hover:text-ink transition-colors">Topics</Link>
          {user && (
            <Link href="/?tab=following" className="link-flourish hover:text-ink transition-colors">Following</Link>
          )}
        </div>

        <div className="flex items-center gap-2.5 sm:gap-3">
          {/* Search */}
          <Link
            href="/search"
            aria-label="Search"
            className="w-9 h-9 rounded-full border border-border text-muted hover:text-ink hover:border-ink transition-colors flex items-center justify-center"
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              <circle cx="11" cy="11" r="7" />
              <path d="m21 21-4.3-4.3" />
            </svg>
          </Link>

          <ThemeToggle />

          {loading ? null : user ? (
            <>
              <NotificationBell />
              <Link
                href="/write"
                className="hidden sm:inline-flex bg-accent hover:bg-accent-hover text-white px-4 py-2 rounded-full transition-colors text-sm font-medium"
              >
                Write
              </Link>

              {/* Avatar menu */}
              <div className="relative" ref={menuRef}>
                <button
                  onClick={() => setMenuOpen((o) => !o)}
                  aria-label="Account menu"
                  aria-expanded={menuOpen}
                  className="flex items-center"
                >
                  <Avatar username={user.username} avatarUrl={user.avatar_url} />
                </button>
                {menuOpen && (
                  <div className="absolute right-0 mt-3 w-52 bg-surface border border-border rounded-xl shadow-lift py-2 text-sm">
                    <p className="px-4 py-2 text-xs uppercase tracking-widest text-muted">
                      @{user.username}
                    </p>
                    {[
                      { href: `/profile/${user.username}`, label: "Profile" },
                      { href: "/dashboard", label: "Dashboard" },
                      { href: "/bookmarks", label: "Reading list" },
                      { href: "/drafts", label: "Drafts" },
                      { href: "/write", label: "Write a story" },
                      ...(isAdmin ? [{ href: "/admin", label: "Admin" }] : []),
                      { href: "/settings", label: "Settings" },
                    ].map((item) => (
                      <Link
                        key={item.href}
                        href={item.href}
                        onClick={() => setMenuOpen(false)}
                        className="block px-4 py-2 text-ink-soft hover:bg-raised hover:text-ink transition-colors"
                      >
                        {item.label}
                      </Link>
                    ))}
                    <button
                      onClick={() => {
                        setMenuOpen(false);
                        logout();
                      }}
                      className="w-full text-left px-4 py-2 text-ink-soft hover:bg-raised hover:text-ink transition-colors"
                    >
                      Sign out
                    </button>
                  </div>
                )}
              </div>
            </>
          ) : (
            <>
              <Link href="/login" className="text-sm text-muted hover:text-ink transition-colors">
                Sign in
              </Link>
              <Link
                href="/register"
                className="bg-accent hover:bg-accent-hover text-white px-4 py-2 rounded-full transition-colors text-sm font-medium"
              >
                Get started
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
