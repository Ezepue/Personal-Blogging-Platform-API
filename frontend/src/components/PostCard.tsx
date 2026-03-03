import Link from "next/link";
import TagBadge from "./TagBadge";

export type Post = {
  id: number;
  title: string;
  content: string;
  tags: string[];
  category?: string | null;
  likes_count: number;
  published_date?: string | null;
  author: { username: string; avatar_url?: string | null };
};

function readTime(content: string): number {
  const words = content.replace(/<[^>]+>/g, "").split(/\s+/).length;
  return Math.max(1, Math.ceil(words / 200));
}

function excerpt(content: string, maxLen = 120): string {
  const plain = content.replace(/<[^>]+>/g, "");
  return plain.length > maxLen ? plain.slice(0, maxLen) + "…" : plain;
}

export default function PostCard({ post }: { post: Post }) {
  const initials = post.author?.username?.[0]?.toUpperCase() ?? "?";

  return (
    <article className="bg-surface border border-border rounded-xl p-6 hover:border-accent transition-colors group">
      {/* Author row */}
      <div className="flex items-center gap-2 mb-3 text-sm text-muted">
        <div className="w-6 h-6 rounded-full bg-accent/20 flex items-center justify-center text-xs font-bold text-accent flex-shrink-0 overflow-hidden">
          {post.author?.avatar_url ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={post.author.avatar_url}
              alt={post.author.username}
              className="w-full h-full object-cover"
            />
          ) : (
            initials
          )}
        </div>
        <span>{post.author?.username ?? "Unknown"}</span>
        <span aria-hidden>·</span>
        <span>{readTime(post.content)} min read</span>
        {post.published_date && (
          <>
            <span aria-hidden>·</span>
            <span>
              {new Date(post.published_date).toLocaleDateString("en-US", {
                month: "short",
                day: "numeric",
                year: "numeric",
              })}
            </span>
          </>
        )}
      </div>

      {/* Title */}
      <Link href={`/posts/${post.id}`}>
        <h2 className="text-xl font-bold text-[#f1f1f5] group-hover:text-accent transition-colors mb-2 line-clamp-2">
          {post.title}
        </h2>
      </Link>

      {/* Excerpt */}
      <p className="text-muted text-sm mb-4 line-clamp-2 leading-relaxed">
        {excerpt(post.content)}
      </p>

      {/* Footer */}
      <div className="flex items-center justify-between">
        <div className="flex flex-wrap gap-1.5">
          {post.tags.slice(0, 3).map((tag) => (
            <TagBadge key={tag} tag={tag} />
          ))}
        </div>
        <span className="text-muted text-sm flex items-center gap-1">
          <span aria-hidden>♥</span>
          <span>{post.likes_count}</span>
        </span>
      </div>
    </article>
  );
}
