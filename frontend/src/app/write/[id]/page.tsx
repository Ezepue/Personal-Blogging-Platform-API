"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";
import dynamic from "next/dynamic";

const Editor = dynamic(() => import("@/components/Editor"), { ssr: false });

export default function EditPage({ params }: { params: { id: string } }) {
  const { id } = params;
  const { user, loading } = useAuth();
  const router = useRouter();

  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [tags, setTags] = useState("");
  const [category, setCategory] = useState("");
  const [status, setStatus] = useState("DRAFT");
  const [saving, setSaving] = useState(false);
  const [fetching, setFetching] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!loading && !user) router.push("/login");
  }, [user, loading, router]);

  useEffect(() => {
    if (!id || loading) return;
    fetch(`/api/articles/${id}`)
      .then((r) => r.json())
      .then((article) => {
        setTitle(article.title ?? "");
        setContent(article.content ?? "");
        setTags(Array.isArray(article.tags) ? article.tags.join(", ") : "");
        setCategory(article.category ?? "");
        setStatus(article.status ?? "DRAFT");
      })
      .catch(() => setError("Failed to load article"))
      .finally(() => setFetching(false));
  }, [id, loading]);

  if (loading || !user || fetching) return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <div className="w-8 h-8 border-2 border-accent border-t-transparent rounded-full animate-spin" />
    </div>
  );

  const submit = async (publish: boolean) => {
    if (!title.trim() || !content.trim()) {
      setError("Title and content are required");
      return;
    }
    setSaving(true);
    setError("");
    try {
      const res = await fetch(`/api/articles/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title,
          content,
          tags: tags.split(",").map((t) => t.trim()).filter(Boolean),
          category: category || undefined,
        }),
      });
      if (res.ok) {
        if (publish && status !== "PUBLISHED") {
          await fetch(`/api/articles/${id}/publish`, { method: "PUT" });
        }
        router.push(`/posts/${id}`);
      } else {
        const err = await res.json().catch(() => ({}));
        setError((err as { detail?: string }).detail ?? "Failed to save");
      }
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto">
      <div className="flex items-center justify-between mb-4">
        <p className="text-xs text-muted">Editing post #{id}</p>
        <Link href="/drafts" className="text-sm text-muted hover:text-[#f1f1f5] transition-colors">
          My Drafts →
        </Link>
      </div>
      <input
        type="text"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="Post title…"
        className="w-full bg-transparent text-4xl font-bold text-[#f1f1f5] placeholder:text-muted outline-none mb-4 border-b border-border pb-4"
      />

      <div className="flex gap-4 mb-4">
        <input
          type="text"
          value={tags}
          onChange={(e) => setTags(e.target.value)}
          placeholder="Tags (comma-separated)"
          className="flex-1 bg-surface border border-border rounded-lg px-3 py-2 text-[#f1f1f5] placeholder:text-muted text-sm focus:outline-none focus:border-accent transition-colors"
        />
        <input
          type="text"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          placeholder="Category"
          className="flex-1 bg-surface border border-border rounded-lg px-3 py-2 text-[#f1f1f5] placeholder:text-muted text-sm focus:outline-none focus:border-accent transition-colors"
        />
      </div>

      <Editor content={content} onChange={setContent} />

      {error && <p className="text-red-400 text-sm mt-3">{error}</p>}

      <div className="flex gap-3 mt-6">
        <button
          onClick={() => submit(false)}
          disabled={saving}
          className="px-5 py-2.5 border border-border rounded-lg text-muted hover:text-[#f1f1f5] hover:border-[#f1f1f5] transition-colors disabled:opacity-50"
        >
          Save Draft
        </button>
        <button
          onClick={() => submit(true)}
          disabled={saving}
          className="px-5 py-2.5 bg-accent hover:bg-accent-hover text-white rounded-lg font-medium transition-colors disabled:opacity-50"
        >
          {saving ? "Saving…" : status === "PUBLISHED" ? "Update" : "Publish"}
        </button>
      </div>
    </div>
  );
}
