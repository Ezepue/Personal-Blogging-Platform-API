import { notFound } from "next/navigation";
import TagBadge from "@/components/TagBadge";
import LikeButton from "@/components/LikeButton";
import CommentSection from "@/components/CommentSection";
import type { Metadata } from "next";

// Always render fresh — never serve stale cached data
export const dynamic = "force-dynamic";

const API_URL = process.env.API_URL ?? "http://localhost:8000";

async function getPost(id: string) {
  try {
    const res = await fetch(`${API_URL}/articles/${id}`, {
      cache: "no-store",
    });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

export async function generateMetadata({
  params,
}: {
  params: { id: string };
}): Promise<Metadata> {
  const post = await getPost(params.id);
  if (!post) return { title: "Post not found" };
  return {
    title: post.title,
    description: post.content.replace(/<[^>]+>/g, "").slice(0, 160),
  };
}

export default async function PostPage({
  params,
}: {
  params: { id: string };
}) {
  const post = await getPost(params.id);
  if (!post) notFound();

  return (
    <article className="max-w-3xl mx-auto">
      {/* Tags */}
      {post.tags?.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mb-6">
          {post.tags.map((tag: string) => (
            <TagBadge key={tag} tag={tag} />
          ))}
        </div>
      )}

      {/* Title */}
      <h1 className="text-4xl font-bold text-[#f1f1f5] mb-4 leading-tight">
        {post.title}
      </h1>

      {/* Author / meta */}
      <div className="flex items-center gap-3 text-muted text-sm mb-8 pb-8 border-b border-border">
        <div className="w-8 h-8 rounded-full bg-accent/20 flex items-center justify-center font-bold text-accent flex-shrink-0 overflow-hidden">
          {post.author?.avatar_url ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={post.author.avatar_url} alt={post.author.username} className="w-full h-full object-cover" />
          ) : (
            post.author?.username?.[0]?.toUpperCase()
          )}
        </div>
        <div>
          <span className="text-[#f1f1f5] font-medium">{post.author?.username}</span>
          {post.published_date && (
            <span className="ml-2">
              {new Date(post.published_date).toLocaleDateString("en-US", {
                year: "numeric",
                month: "long",
                day: "numeric",
              })}
            </span>
          )}
        </div>
      </div>

      {/* Content - NOTE: In production, sanitize with DOMPurify before rendering */}
      <div
        className="prose prose-invert prose-lg max-w-none mb-12
          prose-headings:text-[#f1f1f5]
          prose-p:text-[#c8c8d4]
          prose-a:text-accent
          prose-strong:text-[#f1f1f5]
          prose-code:text-violet-300
          prose-pre:bg-hover
          prose-blockquote:border-accent
          prose-blockquote:text-muted"
        dangerouslySetInnerHTML={{ __html: post.content }}
      />

      {/* Like button */}
      <div className="border-t border-border pt-8 mb-12">
        <LikeButton articleId={post.id} initialCount={post.likes_count ?? 0} />
      </div>

      {/* Comments */}
      <CommentSection articleId={post.id} />
    </article>
  );
}
