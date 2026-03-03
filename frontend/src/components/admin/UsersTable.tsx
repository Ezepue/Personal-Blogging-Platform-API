"use client";

import { useEffect, useState, useCallback } from "react";

const ROLES = ["READER", "AUTHOR", "ADMIN", "SUPER_ADMIN"];

type User = {
  id: number;
  username: string;
  email: string;
  role: string;
};

export default function UsersTable({ isSuperAdmin }: { isSuperAdmin: boolean }) {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState<number | null>(null);
  const [changingRole, setChangingRole] = useState<number | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/admin/users");
      if (res.ok) {
        const data = await res.json();
        setUsers(Array.isArray(data) ? data : []);
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const changeRole = async (userId: number, role: string) => {
    setChangingRole(userId);
    try {
      const res = await fetch(`/api/admin/${userId}/role`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ role }),
      });
      if (res.ok) await load();
    } finally {
      setChangingRole(null);
    }
  };

  const deleteUser = async (id: number) => {
    if (!confirm("Delete this user? All their posts and comments will also be deleted.")) return;
    setDeleting(id);
    try {
      const res = await fetch(`/api/admin/${id}`, { method: "DELETE" });
      if (res.ok) await load();
    } finally {
      setDeleting(null);
    }
  };

  if (loading) return (
    <div className="flex justify-center py-12">
      <div className="w-6 h-6 border-2 border-accent border-t-transparent rounded-full animate-spin" />
    </div>
  );

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border text-left text-muted">
            <th className="py-3 pr-4 font-medium">Username</th>
            <th className="py-3 pr-4 font-medium">Email</th>
            <th className="py-3 pr-4 font-medium">Role</th>
            {isSuperAdmin && <th className="py-3 font-medium"></th>}
          </tr>
        </thead>
        <tbody>
          {users.length === 0 ? (
            <tr>
              <td colSpan={isSuperAdmin ? 4 : 3} className="py-12 text-center text-muted">No users found</td>
            </tr>
          ) : (
            users.map((u) => (
              <tr key={u.id} className="border-b border-border/50 hover:bg-hover transition-colors">
                <td className="py-3 pr-4 text-[#f1f1f5]">{u.username}</td>
                <td className="py-3 pr-4 text-muted">{u.email}</td>
                <td className="py-3 pr-4">
                  {isSuperAdmin ? (
                    <select
                      value={u.role}
                      disabled={changingRole === u.id}
                      onChange={(e) => changeRole(u.id, e.target.value)}
                      className="bg-hover border border-border rounded px-2 py-1 text-[#f1f1f5] text-xs focus:outline-none focus:border-accent disabled:opacity-50"
                    >
                      {ROLES.map((r) => (
                        <option key={r} value={r}>{r}</option>
                      ))}
                    </select>
                  ) : (
                    <span className="text-muted text-xs">{u.role}</span>
                  )}
                </td>
                {isSuperAdmin && (
                  <td className="py-3">
                    <button
                      onClick={() => deleteUser(u.id)}
                      disabled={deleting === u.id}
                      className="text-red-400 hover:text-red-300 text-xs transition-colors disabled:opacity-50"
                    >
                      {deleting === u.id ? "Deleting…" : "Delete"}
                    </button>
                  </td>
                )}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
