"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { avatarColor } from "@/lib/format";
import { api } from "@/lib/api";

type Liker = { id: number; username: string; avatar_url?: string | null };

/** A small stack of reader avatars who liked the article. */
export default function WhoLiked({ articleId }: { articleId: number }) {
  const [likers, setLikers] = useState<Liker[]>([]);

  useEffect(() => {
    api.get<Liker[]>(`/like/${articleId}/users?limit=12`)
      .then((data) => setLikers(Array.isArray(data) ? data : []))
      .catch(() => {});
  }, [articleId]);

  if (likers.length === 0) return null;

  return (
    <div className="flex items-center gap-3">
      <div className="flex -space-x-2">
        {likers.slice(0, 5).map((u) => (
          <Link key={u.id} href={`/profile/${u.username}`} title={u.username}>
            <span
              className="w-7 h-7 rounded-full border-2 border-base flex items-center justify-center text-[10px] font-bold text-white overflow-hidden block"
              style={u.avatar_url ? undefined : { backgroundColor: avatarColor(u.username) }}
            >
              {u.avatar_url ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img src={u.avatar_url} alt={u.username} className="w-full h-full object-cover" />
              ) : (
                u.username[0]?.toUpperCase()
              )}
            </span>
          </Link>
        ))}
      </div>
      <span className="text-xs text-muted">
        Liked by <span className="text-ink-soft font-medium">{likers[0].username}</span>
        {likers.length > 1 && ` and ${likers.length - 1} other${likers.length > 2 ? "s" : ""}`}
      </span>
    </div>
  );
}
