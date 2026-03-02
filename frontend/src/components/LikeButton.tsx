"use client";

import { useState } from "react";
import { useAuth } from "@/contexts/AuthContext";

export default function LikeButton({
  articleId,
  initialCount,
}: {
  articleId: number;
  initialCount: number;
}) {
  const { user } = useAuth();
  const [count, setCount] = useState(initialCount);
  const [liked, setLiked] = useState(false);
  const [loading, setLoading] = useState(false);

  const toggle = async () => {
    if (!user) {
      alert("Sign in to like posts");
      return;
    }
    setLoading(true);
    const method = liked ? "DELETE" : "POST";
    try {
      const res = await fetch(`/api/like/${articleId}`, { method });
      if (res.ok) {
        setLiked(!liked);
        setCount((c) => (liked ? c - 1 : c + 1));
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
      className={`flex items-center gap-2 px-4 py-2 rounded-lg border transition-colors disabled:opacity-50 ${
        liked
          ? "border-red-500 text-red-400 bg-red-500/10"
          : "border-border text-muted hover:border-red-500 hover:text-red-400"
      }`}
    >
      <span aria-hidden>{liked ? "♥" : "♡"}</span>
      <span>
        {count} {count === 1 ? "like" : "likes"}
      </span>
    </button>
  );
}
