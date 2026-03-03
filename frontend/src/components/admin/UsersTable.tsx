"use client";

import { useEffect, useState, useCallback } from "react";

const ASSIGNABLE_ROLES = ["READER", "AUTHOR", "ADMIN"] as const;
type AssignableRole = typeof ASSIGNABLE_ROLES[number];

type User = {
  id: number;
  username: string;
  email: string;
  role: string;
};

const ROLE_STYLES: Record<string, string> = {
  READER:      "bg-sky-500/10 text-sky-400 ring-1 ring-sky-500/20",
  AUTHOR:      "bg-violet-500/10 text-violet-400 ring-1 ring-violet-500/20",
  ADMIN:       "bg-amber-500/10 text-amber-400 ring-1 ring-amber-500/20",
  SUPER_ADMIN: "bg-rose-500/10 text-rose-400 ring-1 ring-rose-500/20",
};

const ROLE_LABELS: Record<string, string> = {
  READER: "Reader",
  AUTHOR: "Author",
  ADMIN: "Admin",
  SUPER_ADMIN: "Super Admin",
};

function Avatar({ name }: { name: string }) {
  return (
    <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-accent/20 text-accent text-xs font-bold shrink-0 select-none">
      {name.slice(0, 2).toUpperCase()}
    </span>
  );
}

function RoleBadge({ role }: { role: string }) {
  const cls = ROLE_STYLES[role] ?? "bg-border/60 text-muted";
  const label = ROLE_LABELS[role] ?? role;
  return (
    <span className={`inline-flex items-center text-xs font-semibold rounded-full px-2.5 py-0.5 ${cls}`}>
      {label}
    </span>
  );
}

function IconSearch() {
  return (
    <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 15.803 7.5 7.5 0 0015.803 15.803z" />
    </svg>
  );
}

function IconTrash() {
  return (
    <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" />
    </svg>
  );
}

function IconError() {
  return (
    <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} className="shrink-0">
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
    </svg>
  );
}

function SkeletonRow({ cols }: { cols: number }) {
  const widths = ["45%", "35%", "15%", "10%"];
  return (
    <tr className="border-b border-border/40">
      {Array.from({ length: cols }).map((_, i) => (
        <td key={i} className="py-3.5 pr-4">
          <div className="h-4 bg-border/50 rounded animate-pulse" style={{ width: widths[i] ?? "10%" }} />
        </td>
      ))}
    </tr>
  );
}

export default function UsersTable({
  isSuperAdmin,
  currentUserId,
}: {
  isSuperAdmin: boolean;
  currentUserId: number;
}) {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState<number | null>(null);
  const [changingRole, setChangingRole] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/admin/users");
      if (res.ok) {
        const data = await res.json();
        setUsers(Array.isArray(data) ? data : []);
      } else {
        setError("Failed to load users");
      }
    } catch {
      setError("Network error — could not load users");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const changeRole = async (userId: number, role: AssignableRole) => {
    setChangingRole(userId);
    setError(null);
    try {
      const res = await fetch(`/api/admin/${userId}/role`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ new_role: role }),
      });
      if (res.ok) {
        await load();
      } else {
        const err = await res.json().catch(() => ({})) as { detail?: string };
        setError(err.detail ?? "Failed to change role");
      }
    } catch {
      setError("Network error — could not change role");
    } finally {
      setChangingRole(null);
    }
  };

  const deleteUser = async (id: number, username: string) => {
    if (!confirm(`Delete "${username}"? All their posts and comments will also be removed. This cannot be undone.`)) return;
    setDeleting(id);
    setError(null);
    try {
      const res = await fetch(`/api/admin/${id}`, { method: "DELETE" });
      if (res.ok) {
        await load();
      } else {
        const err = await res.json().catch(() => ({})) as { detail?: string };
        setError(err.detail ?? "Failed to delete user");
      }
    } catch {
      setError("Network error — could not delete user");
    } finally {
      setDeleting(null);
    }
  };

  const filtered = users.filter((u) => {
    const q = search.toLowerCase();
    return u.username.toLowerCase().includes(q) || u.email.toLowerCase().includes(q);
  });

  const colCount = isSuperAdmin ? 4 : 3;

  return (
    <div className="space-y-4">
      {/* Toolbar */}
      <div className="flex items-center justify-between gap-3">
        <div className="relative flex-1 max-w-xs">
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted pointer-events-none">
            <IconSearch />
          </span>
          <input
            type="text"
            placeholder="Search users…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-3 py-2 bg-hover border border-border rounded-lg text-sm text-[#f1f1f5] placeholder:text-muted focus:outline-none focus:border-accent/60 transition-colors"
          />
        </div>
        <span className="text-muted text-xs shrink-0">
          {loading ? "Loading…" : `${filtered.length} of ${users.length} user${users.length !== 1 ? "s" : ""}`}
        </span>
      </div>

      {/* Error banner */}
      {error && (
        <div className="flex items-center gap-2 text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-4 py-3">
          <IconError />
          {error}
          <button
            onClick={() => setError(null)}
            className="ml-auto text-red-400/60 hover:text-red-400 transition-colors"
          >
            ✕
          </button>
        </div>
      )}

      {/* Table */}
      <div className="overflow-x-auto -mx-1">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border text-left">
              <th className="pb-3 pr-4 text-xs font-semibold text-muted uppercase tracking-wider">User</th>
              <th className="pb-3 pr-4 text-xs font-semibold text-muted uppercase tracking-wider">Email</th>
              <th className="pb-3 pr-4 text-xs font-semibold text-muted uppercase tracking-wider">Role</th>
              {isSuperAdmin && (
                <th className="pb-3 text-xs font-semibold text-muted uppercase tracking-wider text-right">Actions</th>
              )}
            </tr>
          </thead>
          <tbody>
            {loading ? (
              Array.from({ length: 4 }).map((_, i) => <SkeletonRow key={i} cols={colCount} />)
            ) : filtered.length === 0 ? (
              <tr>
                <td colSpan={colCount} className="py-16 text-center">
                  <div className="flex flex-col items-center gap-2 text-muted">
                    <svg width="32" height="32" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.2} className="opacity-40">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 018.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0111.964-3.07M12 6.375a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zm8.25 2.25a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z" />
                    </svg>
                    <p className="text-sm">{search ? "No users match your search" : "No users found"}</p>
                  </div>
                </td>
              </tr>
            ) : (
              filtered.map((u) => {
                const isMe = u.id === currentUserId;
                const isSA = u.role === "SUPER_ADMIN";
                const isChanging = changingRole === u.id;

                return (
                  <tr
                    key={u.id}
                    className="border-b border-border/40 hover:bg-hover/50 transition-colors"
                  >
                    {/* User */}
                    <td className="py-3.5 pr-4">
                      <div className="flex items-center gap-2.5">
                        <Avatar name={u.username} />
                        <div className="flex items-center gap-2 min-w-0">
                          <span className="text-[#f1f1f5] font-medium truncate">{u.username}</span>
                          {isMe && (
                            <span className="text-xs font-semibold text-accent bg-accent/10 rounded-full px-2 py-0.5 shrink-0">
                              You
                            </span>
                          )}
                        </div>
                      </div>
                    </td>

                    {/* Email */}
                    <td className="py-3.5 pr-4 text-muted">{u.email}</td>

                    {/* Role */}
                    <td className="py-3.5 pr-4">
                      {isSuperAdmin && !isMe && !isSA ? (
                        <div className="flex items-center gap-2">
                          <select
                            value={u.role}
                            disabled={isChanging}
                            onChange={(e) => changeRole(u.id, e.target.value as AssignableRole)}
                            className="bg-hover border border-border rounded-lg px-2.5 py-1.5 text-xs font-medium text-[#f1f1f5] focus:outline-none focus:border-accent/60 transition-colors disabled:opacity-50 cursor-pointer"
                          >
                            {ASSIGNABLE_ROLES.map((r) => (
                              <option key={r} value={r}>{r}</option>
                            ))}
                          </select>
                          {isChanging && (
                            <div className="w-3.5 h-3.5 border-2 border-accent border-t-transparent rounded-full animate-spin" />
                          )}
                        </div>
                      ) : (
                        <RoleBadge role={u.role} />
                      )}
                    </td>

                    {/* Actions */}
                    {isSuperAdmin && (
                      <td className="py-3.5 text-right">
                        {!isMe && (
                          <button
                            onClick={() => deleteUser(u.id, u.username)}
                            disabled={deleting === u.id}
                            title="Delete user"
                            className="inline-flex items-center gap-1.5 text-xs text-muted hover:text-red-400 hover:bg-red-500/10 border border-transparent hover:border-red-500/20 rounded-md px-2.5 py-1.5 transition-all disabled:opacity-40 disabled:cursor-not-allowed"
                          >
                            <IconTrash />
                            {deleting === u.id ? "Deleting…" : "Delete"}
                          </button>
                        )}
                      </td>
                    )}
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
