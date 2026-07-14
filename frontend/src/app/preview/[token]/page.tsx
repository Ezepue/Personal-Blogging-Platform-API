import Link from "next/link";
import { notFound } from "next/navigation";
import TagBadge from "@/components/TagBadge";
import { formatDate } from "@/components/PostCard";
import type { Metadata } from "next";

const API_URL = process.env.API_URL ?? "http://localhost:8000";

// Draft previews are private-by-link and must never be indexed.
export const metadata: Metadata = { title: "Draft preview", robots: { index: false, follow: false } };
export const dynamic = "force-dynamic";

async function getPreview(token: string) {
  try {
    const res = await fetch(`${API_URL}/articles/preview/${token}`, { cache: "no-store" });
    return res.ok ? res.json() : null;
  } catch {
    return null;
  }
}

export default async function PreviewPage({ params }: { params: { token: string } }) {
  const post = await getPreview(params.token);
  if (!post) notFound();

  return (
    <article className="max-w-3xl mx-auto">
      <div className="mb-6 rounded-xl border border-accent bg-accent-soft px-4 py-3 text-sm text-accent">
        Draft preview — this link is private and the story isn’t published yet.
      </div>

      <div className="flex flex-wrap items-center gap-1.5 mb-6">
        {post.category && (
          <span className="text-xs uppercase tracking-widest text-accent font-semibold mr-2">{post.category}</span>
        )}
        {post.tags?.map((tag: string) => <TagBadge key={tag} tag={tag} />)}
      </div>

      <h1 className="font-display text-4xl sm:text-5xl leading-[1.1] text-ink mb-4">{post.title}</h1>
      {post.subtitle && <p className="font-display italic text-xl text-muted mb-6">{post.subtitle}</p>}

      <div className="flex items-center gap-3 text-sm text-muted mb-8 pb-8 border-b border-border">
        <span className="text-ink font-medium">{post.author?.username}</span>
        {post.published_date && <span>· {formatDate(post.published_date)}</span>}
        {post.reading_time_minutes ? <span>· {post.reading_time_minutes} min read</span> : null}
      </div>

      {post.cover_image_url && (
        <figure className="mb-10 -mx-4 sm:mx-0">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={post.cover_image_url} alt="" className="w-full max-h-[480px] object-cover sm:rounded-2xl shadow-soft" />
        </figure>
      )}

      {/* Content is server-sanitized at write time. */}
      <div className="article-prose prose-drop mb-12" dangerouslySetInnerHTML={{ __html: post.content }} />

      <Link href="/" className="text-accent hover:underline text-sm">← Back to Quill</Link>
    </article>
  );
}
