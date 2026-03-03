"use client";

import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";
import NotificationBell from "./NotificationBell";
import Logo from "./Logo";

export default function Navbar() {
  const { user, logout, loading } = useAuth();

  return (
    <nav className="bg-surface border-b border-border sticky top-0 z-50">
      <div className="max-w-5xl mx-auto px-4 h-14 flex items-center justify-between">
        {/* Logo */}
        <Logo />

        {/* Nav links */}
        <div className="flex items-center gap-4 text-sm">
          {loading ? null : user ? (
            <>
              <Link
                href="/write"
                className="text-muted hover:text-[#f1f1f5] transition-colors"
              >
                Write
              </Link>
              {(user.role === "AUTHOR" || user.role === "ADMIN" || user.role === "SUPER_ADMIN") && (
                <Link
                  href="/drafts"
                  className="text-muted hover:text-[#f1f1f5] transition-colors"
                >
                  Drafts
                </Link>
              )}
              <NotificationBell />
              <Link
                href={`/profile/${user.username}`}
                className="text-muted hover:text-[#f1f1f5] transition-colors"
              >
                {user.username}
              </Link>
              {(user.role === "ADMIN" || user.role === "SUPER_ADMIN") && (
                <Link
                  href="/admin"
                  className="text-muted hover:text-[#f1f1f5] transition-colors"
                >
                  Admin
                </Link>
              )}
              <Link
                href="/settings"
                className="text-muted hover:text-[#f1f1f5] transition-colors"
              >
                Settings
              </Link>
              <button
                onClick={logout}
                className="text-muted hover:text-[#f1f1f5] transition-colors"
              >
                Sign out
              </button>
            </>
          ) : (
            <>
              <Link
                href="/login"
                className="text-muted hover:text-[#f1f1f5] transition-colors"
              >
                Sign in
              </Link>
              <Link
                href="/register"
                className="bg-accent hover:bg-accent-hover text-white px-3 py-1.5 rounded-lg transition-colors text-sm font-medium"
              >
                Register
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
