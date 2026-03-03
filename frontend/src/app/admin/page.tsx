"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { useRouter } from "next/navigation";
import PostsTable from "@/components/admin/PostsTable";
import UsersTable from "@/components/admin/UsersTable";
import CommentsTable from "@/components/admin/CommentsTable";

type Stats = {
  users: number;
  posts: number;
  comments: number;
  sessions: number;
};

export default function AdminPage() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const [tab, setTab] = useState<"posts" | "users" | "comments">("posts");
  const [stats, setStats] = useState<Stats | null>(null);

  // Role guard
  useEffect(() => {
    if (!loading && (!user || (user.role !== "ADMIN" && user.role !== "SUPER_ADMIN"))) {
      router.push("/");
    }
  }, [user, loading, router]);

  // Load stats
  useEffect(() => {
    if (!user) return;
    Promise.all([
      fetch("/api/admin/users").then((r) => r.ok ? r.json() : []),
      fetch("/api/admin/articles").then((r) => r.ok ? r.json() : []),
      fetch("/api/admin/comments").then((r) => r.ok ? r.json() : []),
      fetch("/api/admin/active-sessions").then((r) => r.ok ? r.json() : []),
    ]).then(([users, posts, comments, sessions]) => {
      setStats({
        users: Array.isArray(users) ? users.length : 0,
        posts: Array.isArray(posts) ? posts.length : 0,
        comments: Array.isArray(comments) ? comments.length : 0,
        sessions: Array.isArray(sessions) ? sessions.length : 0,
      });
    }).catch(() => {/* silently ignore stats load failure */});
  }, [user]);

  if (loading || !user) return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <div className="w-8 h-8 border-2 border-accent border-t-transparent rounded-full animate-spin" />
    </div>
  );

  const isSuperAdmin = user.role === "SUPER_ADMIN";

  const statItems = [
    { label: "Total users", value: stats?.users },
    { label: "Total posts", value: stats?.posts },
    { label: "Total comments", value: stats?.comments },
    { label: "Active sessions", value: stats?.sessions },
  ];

  return (
    <div>
      <h1 className="text-2xl font-bold text-[#f1f1f5] mb-6">Admin Dashboard</h1>

      {/* Stats bar */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {statItems.map((s) => (
          <div key={s.label} className="bg-surface border border-border rounded-xl p-4">
            <p className="text-3xl font-bold text-accent">
              {s.value !== undefined ? s.value : "—"}
            </p>
            <p className="text-muted text-sm mt-1">{s.label}</p>
          </div>
        ))}
      </div>

      {/* Tab bar */}
      <div className="flex gap-1 bg-surface border border-border rounded-lg p-1 mb-6 w-fit">
        {(["posts", "users", "comments"] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 rounded-md text-sm font-medium capitalize transition-colors ${
              tab === t ? "bg-accent text-white" : "text-muted hover:text-[#f1f1f5]"
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div className="bg-surface border border-border rounded-xl p-4">
        {tab === "posts" && <PostsTable />}
        {tab === "users" && <UsersTable isSuperAdmin={isSuperAdmin} />}
        {tab === "comments" && <CommentsTable />}
      </div>
    </div>
  );
}
