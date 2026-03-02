"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import dynamic from "next/dynamic";

const Editor = dynamic(() => import("@/components/Editor"), { ssr: false });

const DRAFT_KEY = "blog_draft";

export default function WritePage() {
  const { user, loading } = useAuth();
  const router = useRouter();

  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [tags, setTags] = useState("");
  const [category, setCategory] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [initialized, setInitialized] = useState(false);

  // Restore draft on mount
  useEffect(() => {
    const saved = localStorage.getItem(DRAFT_KEY);
    if (saved) {
      try {
        const d = JSON.parse(saved);
        setTitle(d.title ?? "");
        setContent(d.content ?? "");
        setTags(d.tags ?? "");
        setCategory(d.category ?? "");
      } catch {
        // ignore malformed draft
      }
    }
    setInitialized(true);
  }, []);

  // Auto-save every 30s
  useEffect(() => {
    const interval = setInterval(() => {
      localStorage.setItem(DRAFT_KEY, JSON.stringify({ title, content, tags, category }));
    }, 30000);
    return () => clearInterval(interval);
  }, [title, content, tags, category]);

  useEffect(() => {
    if (!loading && !user) router.push("/login");
  }, [user, loading, router]);

  if (loading || !user) return null;

  const submit = async (publish: boolean) => {
    if (!title.trim() || !content.trim()) {
      setError("Title and content are required");
      return;
    }
    setSaving(true);
    setError("");
    try {
      const res = await fetch("/api/articles/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title,
          content,
          tags: tags.split(",").map((t) => t.trim()).filter(Boolean),
          category: category || undefined,
        }),
      });
      if (res.ok) {
        const article = await res.json();
        localStorage.removeItem(DRAFT_KEY);
        if (publish) {
          await fetch(`/api/articles/${article.id}/publish`, { method: "PUT" });
        }
        router.push(`/posts/${article.id}`);
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

      {initialized ? (
        <Editor content={content} onChange={setContent} />
      ) : (
        <div className="min-h-[400px] bg-surface border border-border rounded-xl" />
      )}

      {error && <p className="text-red-400 text-sm mt-3">{error}</p>}

      <div className="flex gap-3 mt-6">
        <button
          onClick={() => submit(false)}
          disabled={saving}
          className="px-5 py-2.5 border border-border rounded-lg text-muted hover:text-[#f1f1f5] hover:border-[#f1f1f5] transition-colors disabled:opacity-50"
        >
          {saving ? "Saving…" : "Save Draft"}
        </button>
        <button
          onClick={() => submit(true)}
          disabled={saving}
          className="px-5 py-2.5 bg-accent hover:bg-accent-hover text-white rounded-lg font-medium transition-colors disabled:opacity-50"
        >
          {saving ? "Publishing…" : "Publish"}
        </button>
      </div>
    </div>
  );
}
