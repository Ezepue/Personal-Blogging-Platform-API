import Link from "next/link";
import TagBadge from "./TagBadge";

export type Post = {
  id: number;
  title: string;
  subtitle?: string | null;
  content: string;
  tags: string[];
  category?: string | null;
  cover_image_url?: string | null;
  likes_count: number;
  views_count?: number;
  reading_time_minutes?: number;
  published_date?: string | null;
  author?: { username: string; avatar_url?: string | null } | null;
};

export function excerpt(post: Post, maxLen = 150): string {
  if (post.subtitle) return post.subtitle;
  const plain = post.content.replace(/<[^>]+>/g, "").trim();
  return plain.length > maxLen ? plain.slice(0, maxLen) + "…" : plain;
}

export function formatDate(date?: string | null): string {
  if (!date) return "";
  return new Date(date).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export default function PostCard({ post, large = false }: { post: Post; large?: boolean }) {
  const username = post.author?.username ?? "unknown";
  const initials = username[0]?.toUpperCase() ?? "?";

  return (
    <article
      className={`card-lift bg-surface border border-border rounded-2xl overflow-hidden shadow-soft flex flex-col ${
        large ? "md:flex-row" : ""
      }`}
    >
      {post.cover_image_url && (
        <Link
          href={`/posts/${post.id}`}
          className={`block overflow-hidden bg-raised ${large ? "md:w-1/2 md:min-h-[280px]" : "h-44"}`}
        >
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={post.cover_image_url}
            alt=""
            className="w-full h-full object-cover"
          />
        </Link>
      )}

      <div className={`p-6 flex flex-col flex-1 ${large ? "md:p-9 justify-center" : ""}`}>
        {/* Author row */}
        <div className="flex items-center gap-2 mb-3 text-xs text-muted">
          <Link href={`/profile/${username}`} className="flex items-center gap-2 hover:text-ink transition-colors">
            <span className="w-6 h-6 rounded-full bg-accent-soft flex items-center justify-center text-[10px] font-bold text-accent shrink-0 overflow-hidden">
              {post.author?.avatar_url ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img src={post.author.avatar_url} alt={username} className="w-full h-full object-cover" />
              ) : (
                initials
              )}
            </span>
            <span className="font-medium">{username}</span>
          </Link>
          {post.published_date && (
            <>
              <span aria-hidden>·</span>
              <span>{formatDate(post.published_date)}</span>
            </>
          )}
          {post.reading_time_minutes ? (
            <>
              <span aria-hidden>·</span>
              <span>{post.reading_time_minutes} min read</span>
            </>
          ) : null}
        </div>

        {/* Title + excerpt */}
        <Link href={`/posts/${post.id}`} className="group">
          <h2
            className={`font-display text-ink group-hover:text-accent transition-colors leading-snug mb-2 ${
              large ? "text-3xl md:text-4xl" : "text-xl"
            } line-clamp-2`}
          >
            {post.title}
          </h2>
          <p className={`text-muted leading-relaxed mb-4 ${large ? "text-base line-clamp-3" : "text-sm line-clamp-2"}`}>
            {excerpt(post)}
          </p>
        </Link>

        {/* Footer */}
        <div className="mt-auto flex items-center justify-between gap-3">
          <div className="flex flex-wrap gap-1.5 min-w-0">
            {post.tags.slice(0, 3).map((tag) => (
              <TagBadge key={tag} tag={tag} />
            ))}
          </div>
          <div className="flex items-center gap-3 text-xs text-muted shrink-0">
            {typeof post.views_count === "number" && (
              <span className="flex items-center gap-1" title="Views">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7Z" />
                  <circle cx="12" cy="12" r="3" />
                </svg>
                {post.views_count}
              </span>
            )}
            <span className="flex items-center gap-1" title="Likes">
              <span aria-hidden>♥</span>
              {post.likes_count}
            </span>
          </div>
        </div>
      </div>
    </article>
  );
}
