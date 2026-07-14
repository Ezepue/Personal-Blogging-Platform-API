"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";

export default function FollowButton({
  username,
  initialFollowing = false,
  onCountChange,
}: {
  username: string;
  initialFollowing?: boolean;
  onCountChange?: (count: number) => void;
}) {
  const { user } = useAuth();
  const router = useRouter();
  const [following, setFollowing] = useState(initialFollowing);
  const [busy, setBusy] = useState(false);

  // The server can't know the viewer's follow state on cached pages — hydrate it.
  useEffect(() => {
    if (!user || user.username === username) return;
    let cancelled = false;
    fetch(`/api/users/${username}/profile`)
      .then((r) => (r.ok ? r.json() : null))
      .then((p) => {
        if (!cancelled && p) setFollowing(Boolean(p.is_followed_by_me));
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [user, username]);

  if (user?.username === username) return null;

  const toggle = async () => {
    if (!user) {
      router.push("/login");
      return;
    }
    if (busy) return;
    setBusy(true);
    try {
      const res = await fetch(`/api/users/${username}/follow`, {
        method: following ? "DELETE" : "POST",
      });
      if (res.ok) {
        const data = await res.json();
        setFollowing(!following);
        if (typeof data.followers_count === "number") onCountChange?.(data.followers_count);
      }
    } finally {
      setBusy(false);
    }
  };

  return (
    <button
      onClick={toggle}
      disabled={busy}
      className={`px-5 py-2 rounded-full text-sm font-medium transition-colors disabled:opacity-60 ${
        following
          ? "border border-border text-muted hover:text-ink hover:border-ink"
          : "bg-accent hover:bg-accent-hover text-white"
      }`}
    >
      {following ? "Following" : "Follow"}
    </button>
  );
}
