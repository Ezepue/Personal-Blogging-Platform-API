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

function IconUsers() {
  return (
    <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 018.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0111.964-3.07M12 6.375a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zm8.25 2.25a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z" />
    </svg>
  );
}

function IconDoc() {
  return (
    <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
    </svg>
  );
}

function IconChat() {
  return (
    <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M7.5 8.25h9m-9 3H12m-9.75 1.51c0 1.6 1.123 2.994 2.707 3.227 1.129.166 2.27.293 3.423.379.35.026.67.21.865.501L12 21l2.755-4.133a1.14 1.14 0 01.865-.501 48.172 48.172 0 003.423-.379c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0012 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018z" />
    </svg>
  );
}

function IconBolt() {
  return (
    <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
    </svg>
  );
}

function IconShield() {
  return (
    <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
    </svg>
  );
}

type TabKey = "posts" | "users" | "comments";

export default function AdminPage() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const [tab, setTab] = useState<TabKey>("posts");
  const [stats, setStats] = useState<Stats | null>(null);

  const isSuperAdmin = user?.role === "SUPER_ADMIN";

  useEffect(() => {
    if (!loading && (!user || (user.role !== "ADMIN" && user.role !== "SUPER_ADMIN"))) {
      router.push("/");
    }
  }, [user, loading, router]);

  useEffect(() => {
    if (!isSuperAdmin && tab === "users") setTab("posts");
  }, [isSuperAdmin, tab]);

  useEffect(() => {
    if (!user) return;
    const fetches = [
      fetch("/api/admin/articles").then((r) => r.ok ? r.json() : []),
      fetch("/api/admin/comments").then((r) => r.ok ? r.json() : []),
      fetch("/api/admin/active-sessions").then((r) => r.ok ? r.json() : []),
    ];
    if (isSuperAdmin) {
      fetches.unshift(fetch("/api/admin/users").then((r) => r.ok ? r.json() : []));
      Promise.all(fetches).then(([users, posts, comments, sessions]) => {
        setStats({
          users: Array.isArray(users) ? users.length : 0,
          posts: Array.isArray(posts) ? posts.length : 0,
          comments: Array.isArray(comments) ? comments.length : 0,
          sessions: Array.isArray(sessions) ? sessions.length : 0,
        });
      }).catch(() => {});
    } else {
      Promise.all(fetches).then(([posts, comments, sessions]) => {
        setStats({
          users: 0,
          posts: Array.isArray(posts) ? posts.length : 0,
          comments: Array.isArray(comments) ? comments.length : 0,
          sessions: Array.isArray(sessions) ? sessions.length : 0,
        });
      }).catch(() => {});
    }
  }, [user, isSuperAdmin]);

  if (loading || !user || (user.role !== "ADMIN" && user.role !== "SUPER_ADMIN")) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="w-7 h-7 border-2 border-accent border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  const tabs: { key: TabKey; label: string; count?: number }[] = [
    { key: "posts", label: "Posts", count: stats?.posts },
    ...(isSuperAdmin ? [{ key: "users" as TabKey, label: "Users", count: stats?.users }] : []),
    { key: "comments", label: "Comments", count: stats?.comments },
  ];

  const statCards = [
    ...(isSuperAdmin
      ? [{
          label: "Total Users",
          value: stats?.users,
          icon: <IconUsers />,
          color: "text-sky-400",
          ring: "ring-sky-500/20",
          bg: "bg-sky-500/10",
        }]
      : []),
    {
      label: "Total Posts",
      value: stats?.posts,
      icon: <IconDoc />,
      color: "text-violet-400",
      ring: "ring-violet-500/20",
      bg: "bg-violet-500/10",
    },
    {
      label: "Comments",
      value: stats?.comments,
      icon: <IconChat />,
      color: "text-emerald-400",
      ring: "ring-emerald-500/20",
      bg: "bg-emerald-500/10",
    },
    {
      label: "Active Sessions",
      value: stats?.sessions,
      icon: <IconBolt />,
      color: "text-amber-400",
      ring: "ring-amber-500/20",
      bg: "bg-amber-500/10",
    },
  ];

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Page header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="inline-flex items-center gap-1.5 text-xs font-semibold text-accent bg-accent/10 border border-accent/20 rounded-full px-3 py-1">
              <IconShield />
              {isSuperAdmin ? "Super Admin" : "Admin"}
            </span>
          </div>
          <h1 className="text-3xl font-bold text-[#f1f1f5] tracking-tight">Dashboard</h1>
          <p className="text-muted text-sm mt-1">
            Welcome back, <span className="text-[#f1f1f5] font-medium">{user.username}</span>
          </p>
        </div>
      </div>

      {/* Stat cards */}
      <div className={`grid gap-4 ${isSuperAdmin ? "grid-cols-2 xl:grid-cols-4" : "grid-cols-3"}`}>
        {statCards.map((card) => (
          <div
            key={card.label}
            className={`bg-surface border border-border rounded-2xl p-5 flex items-center gap-4 ring-1 ${card.ring} hover:border-border/80 transition-all group`}
          >
            <div className={`${card.bg} ${card.color} rounded-xl p-3 shrink-0 transition-transform group-hover:scale-110`}>
              {card.icon}
            </div>
            <div className="min-w-0">
              <p className={`text-2xl font-bold leading-none ${card.color}`}>
                {card.value !== undefined
                  ? card.value.toLocaleString()
                  : <span className="text-border text-lg">—</span>}
              </p>
              <p className="text-muted text-xs mt-1 truncate">{card.label}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Tab panel */}
      <div className="bg-surface border border-border rounded-2xl overflow-hidden">
        {/* Tab bar */}
        <div className="flex border-b border-border bg-hover/30 px-4">
          {tabs.map(({ key, label, count }) => (
            <button
              key={key}
              onClick={() => setTab(key)}
              className={`relative flex items-center gap-2 px-4 py-4 text-sm font-medium transition-colors ${
                tab === key
                  ? "text-[#f1f1f5]"
                  : "text-muted hover:text-[#f1f1f5]"
              }`}
            >
              {label}
              {count !== undefined && (
                <span className={`text-xs rounded-full px-2 py-0.5 font-semibold ${
                  tab === key
                    ? "bg-accent/20 text-accent"
                    : "bg-border/80 text-muted"
                }`}>
                  {count.toLocaleString()}
                </span>
              )}
              {tab === key && (
                <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-accent rounded-t-full" />
              )}
            </button>
          ))}
        </div>

        {/* Panel body */}
        <div className="p-5">
          {tab === "posts" && <PostsTable />}
          {tab === "users" && isSuperAdmin && (
            <UsersTable isSuperAdmin={isSuperAdmin} currentUserId={user.id} />
          )}
          {tab === "comments" && <CommentsTable />}
        </div>
      </div>
    </div>
  );
}
