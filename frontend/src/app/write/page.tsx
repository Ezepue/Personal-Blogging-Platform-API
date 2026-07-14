"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";
import dynamic from "next/dynamic";
import CoverImagePicker from "@/components/CoverImagePicker";

const Editor = dynamic(() => import("@/components/Editor"), { ssr: false });

const DRAFT_KEY = "blog_draft";

export default function WritePage() {
  const { user, loading } = useAuth();
  const router = useRouter();

  const [title, setTitle] = useState("");
  const [subtitle, setSubtitle] = useState("");
  const [content, setContent] = useState("");
  const [tags, setTags] = useState("");
  const [category, setCategory] = useState("");
  const [coverUrl, setCoverUrl] = useState("");
  const [unlisted, setUnlisted] = useState(false);
  const [savingAction, setSavingAction] = useState<"draft" | "publish" | null>(null);
  const [error, setError] = useState("");
  const [initialized, setInitialized] = useState(false);

  // Restore draft on mount
  useEffect(() => {
    const saved = localStorage.getItem(DRAFT_KEY);
    if (saved) {
      try {
        const d = JSON.parse(saved);
        setTitle(d.title ?? "");
        setSubtitle(d.subtitle ?? "");
        setContent(d.content ?? "");
        setTags(d.tags ?? "");
        setCategory(d.category ?? "");
        setCoverUrl(d.coverUrl ?? "");
        setUnlisted(Boolean(d.unlisted));
      } catch {
        // ignore malformed draft
      }
    }
    setInitialized(true);
  }, []);

  // Auto-save every 30s
  useEffect(() => {
    const interval = setInterval(() => {
      localStorage.setItem(
        DRAFT_KEY,
        JSON.stringify({ title, subtitle, content, tags, category, coverUrl, unlisted })
      );
    }, 30000);
    return () => clearInterval(interval);
  }, [title, subtitle, content, tags, category, coverUrl, unlisted]);

  useEffect(() => {
    if (!loading && !user) router.push("/login");
  }, [user, loading, router]);

  if (loading || !user) return null;

  const submit = async (publish: boolean) => {
    if (!title.trim() || !content.trim()) {
      setError("Title and content are required");
      return;
    }
    setSavingAction(publish ? "publish" : "draft");
    setError("");
    try {
      const res = await fetch("/api/articles/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title,
          subtitle: subtitle.trim() || null,
          content,
          tags: tags.split(",").map((t) => t.trim()).filter(Boolean),
          category: category || undefined,
          cover_image_url: coverUrl || null,
          is_unlisted: unlisted,
          status: publish ? "published" : "draft",
        }),
      });
      if (res.ok) {
        const article = await res.json();
        localStorage.removeItem(DRAFT_KEY);
        router.push(publish ? `/posts/${article.id}` : `/write/${article.id}`);
      } else {
        const err = await res.json().catch(() => ({}));
        setError((err as { detail?: string }).detail ?? "Failed to save");
      }
    } finally {
      setSavingAction(null);
    }
  };

  return (
    <div className="max-w-3xl mx-auto">
      {/* Top bar */}
      <div className="flex items-center justify-between mb-8">
        <p className="text-xs uppercase tracking-[0.3em] text-muted">New story</p>
        <Link href="/drafts" className="text-sm text-muted hover:text-ink transition-colors link-flourish">
          My drafts →
        </Link>
      </div>

      <CoverImagePicker value={coverUrl} onChange={setCoverUrl} />

      <input
        type="text"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="Title…"
        className="w-full bg-transparent font-display text-4xl sm:text-5xl text-ink placeholder:text-muted outline-none mb-3"
      />
      <input
        type="text"
        value={subtitle}
        onChange={(e) => setSubtitle(e.target.value)}
        placeholder="A short subtitle (optional)…"
        maxLength={300}
        className="w-full bg-transparent font-display italic text-xl text-ink-soft placeholder:text-muted outline-none mb-6 border-b border-border pb-5"
      />

      <div className="flex gap-4 mb-5">
        <input
          type="text"
          value={tags}
          onChange={(e) => setTags(e.target.value)}
          placeholder="Tags (comma-separated)"
          className="flex-1 bg-surface border border-border rounded-lg px-3 py-2 text-ink placeholder:text-muted text-sm focus:outline-none focus:border-accent transition-colors"
        />
        <input
          type="text"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          placeholder="Category"
          className="flex-1 bg-surface border border-border rounded-lg px-3 py-2 text-ink placeholder:text-muted text-sm focus:outline-none focus:border-accent transition-colors"
        />
      </div>

      {initialized ? (
        <Editor content={content} onChange={setContent} />
      ) : (
        <div className="min-h-[400px] bg-surface border border-border rounded-xl" />
      )}

      <label className="flex items-center gap-2 mt-4 text-sm text-muted cursor-pointer w-fit">
        <input type="checkbox" checked={unlisted} onChange={(e) => setUnlisted(e.target.checked)} className="w-4 h-4 accent-[var(--accent)]" />
        Unlisted — reachable by link, hidden from feeds and search
      </label>

      {error && <p className="text-red-400 text-sm mt-3">{error}</p>}

      <div className="flex gap-3 mt-6">
        <button
          onClick={() => submit(false)}
          disabled={savingAction !== null}
          className="px-5 py-2.5 border border-border rounded-full text-muted hover:text-ink hover:border-ink transition-colors disabled:opacity-50"
        >
          {savingAction === "draft" ? "Saving…" : "Save draft"}
        </button>
        <button
          onClick={() => submit(true)}
          disabled={savingAction !== null}
          className="px-5 py-2.5 bg-accent hover:bg-accent-hover text-white rounded-full font-medium transition-colors disabled:opacity-50"
        >
          {savingAction === "publish" ? "Publishing…" : "Publish"}
        </button>
      </div>
    </div>
  );
}
