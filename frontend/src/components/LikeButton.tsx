"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";

export default function LikeButton({
  articleId,
  initialCount,
}: {
  articleId: number;
  initialCount: number;
}) {
  const { user } = useAuth();
  const router = useRouter();
  const [count, setCount] = useState(initialCount);
  const [liked, setLiked] = useState(false);
  const [loading, setLoading] = useState(false);

  // Reflect the current user's like state (and authoritative count) on mount.
  useEffect(() => {
    if (!user) {
      setLiked(false);
      return;
    }
    let cancelled = false;
    fetch(`/api/like/${articleId}/status`)
      .then((r) => (r.ok ? r.json() : null))
      .then((data) => {
        if (cancelled || !data) return;
        setLiked(Boolean(data.liked));
        if (typeof data.likes_count === "number") setCount(data.likes_count);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [articleId, user]);

  const [pop, setPop] = useState(false);

  const toggle = async () => {
    if (!user) {
      router.push("/login");
      return;
    }
    if (loading) return;
    setLoading(true);
    const method = liked ? "DELETE" : "POST";
    try {
      const res = await fetch(`/api/like/${articleId}`, { method });
      if (res.ok) {
        const nowLiked = !liked;
        setLiked(nowLiked);
        setCount((c) => (liked ? Math.max(0, c - 1) : c + 1));
        if (nowLiked) {
          setPop(true);
          setTimeout(() => setPop(false), 340);
        }
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      onClick={toggle}
      disabled={loading}
      aria-label={`${liked ? "Unlike" : "Like"} this post`}
      aria-pressed={liked}
      className={`flex items-center gap-2 px-4 py-2 rounded-full border transition-colors disabled:opacity-50 ${
        liked
          ? "border-accent text-accent bg-accent-soft"
          : "border-border text-muted hover:border-accent hover:text-accent"
      }`}
    >
      <span aria-hidden className={pop ? "heart-pop" : ""}>{liked ? "♥" : "♡"}</span>
      <span>
        {count} {count === 1 ? "like" : "likes"}
      </span>
    </button>
  );
}
