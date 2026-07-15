"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { useToast } from "@/components/ui/Toast";

export default function BookmarkButton({ articleId }: { articleId: number }) {
  const { user } = useAuth();
  const router = useRouter();
  const { toast } = useToast();
  const [saved, setSaved] = useState(false);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!user) {
      setSaved(false);
      return;
    }
    let cancelled = false;
    fetch(`/api/bookmarks/${articleId}/status`)
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => {
        if (!cancelled && d) setSaved(Boolean(d.bookmarked));
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [articleId, user]);

  const toggle = async () => {
    if (!user) {
      router.push("/login");
      return;
    }
    if (busy) return;
    setBusy(true);
    const wasSaved = saved;
    try {
      const res = await fetch(`/api/bookmarks/${articleId}`, {
        method: wasSaved ? "DELETE" : "POST",
      });
      if (res.ok) {
        setSaved(!wasSaved);
        if (wasSaved) {
          toast("Removed from reading list", "info", { label: "Undo", onClick: undo });
        } else {
          toast("Saved to reading list", "success");
        }
      }
    } finally {
      setBusy(false);
    }
  };

  const undo = async () => {
    const res = await fetch(`/api/bookmarks/${articleId}`, { method: "POST" });
    if (res.ok) setSaved(true);
  };

  return (
    <button
      onClick={toggle}
      disabled={busy}
      aria-label={saved ? "Remove bookmark" : "Save to reading list"}
      title={saved ? "Remove bookmark" : "Save to reading list"}
      className={`flex items-center gap-2 px-4 py-2 rounded-full border transition-colors disabled:opacity-60 text-sm ${
        saved
          ? "border-accent text-accent bg-accent-soft"
          : "border-border text-muted hover:border-accent hover:text-accent"
      }`}
    >
      <svg width="14" height="14" viewBox="0 0 24 24" fill={saved ? "currentColor" : "none"} stroke="currentColor" strokeWidth="2" strokeLinejoin="round">
        <path d="M6 3h12a1 1 0 0 1 1 1v17l-7-4-7 4V4a1 1 0 0 1 1-1Z" />
      </svg>
      {saved ? "Saved" : "Save"}
    </button>
  );
}
