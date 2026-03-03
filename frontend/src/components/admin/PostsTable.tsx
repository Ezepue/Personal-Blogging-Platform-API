"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";

type Post = {
  id: number;
  title: string;
  status: string;
  published_date: string | null;
  author?: { username: string };
};

export default function PostsTable() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState<number | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/admin/articles");
      if (res.ok) {
        const data = await res.json();
        setPosts(Array.isArray(data) ? data : []);
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const deletePost = async (id: number) => {
    if (!confirm("Delete this post permanently?")) return;
    setDeleting(id);
    try {
      const res = await fetch(`/api/admin/articles/${id}`, { method: "DELETE" });
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
            <th className="py-3 pr-4 font-medium">Title</th>
            <th className="py-3 pr-4 font-medium">Author</th>
            <th className="py-3 pr-4 font-medium">Status</th>
            <th className="py-3 pr-4 font-medium">Date</th>
            <th className="py-3 font-medium"></th>
          </tr>
        </thead>
        <tbody>
          {posts.length === 0 ? (
            <tr>
              <td colSpan={5} className="py-12 text-center text-muted">No posts found</td>
            </tr>
          ) : (
            posts.map((p) => (
              <tr key={p.id} className="border-b border-border/50 hover:bg-hover transition-colors">
                <td className="py-3 pr-4 text-[#f1f1f5] max-w-xs">
                  <Link href={`/posts/${p.id}`} className="hover:text-accent transition-colors truncate block">
                    {p.title}
                  </Link>
                </td>
                <td className="py-3 pr-4 text-muted">{p.author?.username ?? "—"}</td>
                <td className="py-3 pr-4">
                  <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                    p.status === "PUBLISHED"
                      ? "bg-green-900/50 text-green-300"
                      : "bg-gray-800 text-gray-400"
                  }`}>
                    {p.status}
                  </span>
                </td>
                <td className="py-3 pr-4 text-muted text-xs">
                  {p.published_date ? new Date(p.published_date).toLocaleDateString() : "—"}
                </td>
                <td className="py-3">
                  <button
                    onClick={() => deletePost(p.id)}
                    disabled={deleting === p.id}
                    className="text-red-400 hover:text-red-300 text-xs transition-colors disabled:opacity-50"
                  >
                    {deleting === p.id ? "Deleting…" : "Delete"}
                  </button>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
