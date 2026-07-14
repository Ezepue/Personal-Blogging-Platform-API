"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";
import dynamic from "next/dynamic";
import CoverImagePicker from "@/components/CoverImagePicker";

const Editor = dynamic(() => import("@/components/Editor"), { ssr: false });

export default function EditPage({ params }: { params: { id: string } }) {
  const { id } = params;
  const { user, loading } = useAuth();
  const router = useRouter();

  const [title, setTitle] = useState("");
  const [subtitle, setSubtitle] = useState("");
  const [content, setContent] = useState("");
  const [tags, setTags] = useState("");
  const [category, setCategory] = useState("");
  const [coverUrl, setCoverUrl] = useState("");
  const [status, setStatus] = useState("draft");
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
        setSubtitle(article.subtitle ?? "");
        setContent(article.content ?? "");
        setTags(Array.isArray(article.tags) ? article.tags.join(", ") : "");
        setCategory(article.category ?? "");
        setCoverUrl(article.cover_image_url ?? "");
        setStatus(article.status ?? "draft");
      })
      .catch(() => setError("Failed to load article"))
      .finally(() => setFetching(false));
  }, [id, loading]);

  if (loading || !user || fetching)
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="w-8 h-8 border-2 border-accent border-t-transparent rounded-full animate-spin" />
      </div>
    );

  const isPublished = status.toLowerCase() === "published";

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
          subtitle: subtitle.trim() || null,
          content,
          tags: tags.split(",").map((t) => t.trim()).filter(Boolean),
          category: category || undefined,
          cover_image_url: coverUrl || null,
        }),
      });
      if (res.ok) {
        if (publish && !isPublished) {
          const pub = await fetch(`/api/articles/${id}/publish`, { method: "PUT" });
          if (!pub.ok) {
            setError("Saved, but publishing failed. Try publishing again.");
            return;
          }
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
      <div className="flex items-center justify-between mb-8">
        <p className="text-xs uppercase tracking-[0.3em] text-muted">
          Editing · {isPublished ? "published" : "draft"}
        </p>
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

      <Editor content={content} onChange={setContent} />

      {error && <p className="text-red-400 text-sm mt-3">{error}</p>}

      <div className="flex gap-3 mt-6">
        <button
          onClick={() => submit(false)}
          disabled={saving}
          className="px-5 py-2.5 border border-border rounded-full text-muted hover:text-ink hover:border-ink transition-colors disabled:opacity-50"
        >
          Save draft
        </button>
        <button
          onClick={() => submit(true)}
          disabled={saving}
          className="px-5 py-2.5 bg-accent hover:bg-accent-hover text-white rounded-full font-medium transition-colors disabled:opacity-50"
        >
          {saving ? "Saving…" : isPublished ? "Update" : "Publish"}
        </button>
      </div>
    </div>
  );
}
