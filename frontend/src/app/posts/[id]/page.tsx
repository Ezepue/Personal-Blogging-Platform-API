import Link from "next/link";
import { notFound } from "next/navigation";
import TagBadge from "@/components/TagBadge";
import LikeButton from "@/components/LikeButton";
import CommentSection from "@/components/CommentSection";
import BookmarkButton from "@/components/BookmarkButton";
import FollowButton from "@/components/FollowButton";
import ShareRow from "@/components/ShareRow";
import ReadingProgress from "@/components/ReadingProgress";
import TableOfContents from "@/components/TableOfContents";
import ArticleEnhancer from "@/components/ArticleEnhancer";
import VerifiedBadge from "@/components/VerifiedBadge";
import WhoLiked from "@/components/WhoLiked";
import PostCard, { Post, formatDate } from "@/components/PostCard";
import type { Metadata } from "next";

const API_URL = process.env.API_URL ?? "http://localhost:8000";
const SITE_URL = process.env.SITE_URL ?? "http://localhost:3000";

async function getAuthorPosts(username: string, excludeId: number): Promise<Post[]> {
  try {
    const res = await fetch(`${API_URL}/users/${username}/articles?limit=4`, {
      next: { revalidate: 120 },
    });
    if (!res.ok) return [];
    const posts: Post[] = await res.json();
    return posts.filter((p) => p.id !== excludeId).slice(0, 3);
  } catch {
    return [];
  }
}

async function getPost(id: string) {
  try {
    const res = await fetch(`${API_URL}/articles/${id}`, {
      next: { revalidate: 60 },
    });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

async function getRelated(id: string): Promise<Post[]> {
  try {
    const res = await fetch(`${API_URL}/articles/${id}/related?limit=3`, {
      next: { revalidate: 120 },
    });
    return res.ok ? res.json() : [];
  } catch {
    return [];
  }
}

export async function generateMetadata({
  params,
}: {
  params: { id: string };
}): Promise<Metadata> {
  const post = await getPost(params.id);
  if (!post) return { title: "Post not found" };
  const description =
    post.subtitle ?? post.content.replace(/<[^>]+>/g, "").slice(0, 160);
  return {
    title: post.title,
    description,
    openGraph: {
      title: post.title,
      description,
      type: "article",
      publishedTime: post.published_date ?? undefined,
      authors: post.author?.username ? [post.author.username] : undefined,
      images: post.cover_image_url ? [{ url: post.cover_image_url }] : undefined,
    },
    twitter: {
      card: post.cover_image_url ? "summary_large_image" : "summary",
      title: post.title,
      description,
    },
  };
}

export default async function PostPage({
  params,
}: {
  params: { id: string };
}) {
  const post = await getPost(params.id);
  if (!post) notFound();

  const username: string = post.author?.username ?? "unknown";
  const [related, authorPosts] = await Promise.all([
    getRelated(params.id),
    getAuthorPosts(username, post.id),
  ]);

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "Article",
    headline: post.title,
    description: post.subtitle ?? undefined,
    image: post.cover_image_url ? [post.cover_image_url] : undefined,
    datePublished: post.published_date ?? undefined,
    dateModified: post.updated_date ?? undefined,
    author: { "@type": "Person", name: username, url: `${SITE_URL}/profile/${username}` },
    mainEntityOfPage: `${SITE_URL}/posts/${post.id}`,
    wordCount: post.word_count || undefined,
  };

  // Escape "<" so a title/subtitle containing "</script>" cannot break out of
  // the JSON-LD script element (JSON.stringify does not escape it).
  const jsonLdSafe = JSON.stringify(jsonLd).replace(/</g, "\\u003c");

  return (
    <>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: jsonLdSafe }} />
      <ReadingProgress />

      <div className="xl:grid xl:grid-cols-[1fr_16rem] xl:gap-12">
        <article className="max-w-3xl mx-auto xl:mx-0 xl:justify-self-end w-full">
          {/* Kicker: tags + category */}
          <div className="flex flex-wrap items-center gap-1.5 mb-6 fade-up">
            {post.category && (
              <span className="text-xs uppercase tracking-widest text-accent font-semibold mr-2">
                {post.category}
              </span>
            )}
            {post.tags?.map((tag: string) => <TagBadge key={tag} tag={tag} />)}
          </div>

          {/* Title + subtitle */}
          <h1 className="font-display text-4xl sm:text-5xl leading-[1.1] text-ink mb-4 fade-up">
            {post.title}
          </h1>
          {post.subtitle && (
            <p className="font-display italic text-xl text-muted mb-6 leading-relaxed fade-up fade-up-1">
              {post.subtitle}
            </p>
          )}

          {/* Meta row */}
          <div className="flex flex-wrap items-center justify-between gap-4 text-sm text-muted mb-8 pb-8 border-b border-border fade-up fade-up-1">
            <div className="flex items-center gap-3">
              <Link href={`/profile/${username}`} className="flex items-center gap-3 group">
                <span className="w-9 h-9 rounded-full bg-accent-soft flex items-center justify-center font-bold text-accent shrink-0 overflow-hidden">
                  {post.author?.avatar_url ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img src={post.author.avatar_url} alt={username} className="w-full h-full object-cover" />
                  ) : (
                    username[0]?.toUpperCase()
                  )}
                </span>
                <span>
                  <span className="flex items-center gap-1 text-ink font-medium group-hover:text-accent transition-colors">
                    {username}
                    {post.author?.is_verified && <VerifiedBadge />}
                  </span>
                  <span className="block text-xs">
                    {post.published_date && formatDate(post.published_date)}
                    {post.reading_time_minutes ? ` · ${post.reading_time_minutes} min read` : ""}
                    {typeof post.views_count === "number" ? ` · ${post.views_count} views` : ""}
                  </span>
                </span>
              </Link>
            </div>
            <div className="flex items-center gap-2">
              <ArticleEnhancer targetId="article-body" />
              <BookmarkButton articleId={post.id} />
              <ShareRow title={post.title} />
            </div>
          </div>

          {/* Cover image */}
          {post.cover_image_url && (
            <figure className="mb-10 -mx-4 sm:mx-0 fade-up fade-up-2">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={post.cover_image_url}
                alt=""
                className="w-full max-h-[480px] object-cover sm:rounded-2xl shadow-soft"
              />
            </figure>
          )}

          {/* Content is sanitized server-side (utils/sanitize.py) at write time, so the
              stored HTML is safe to render here. */}
          <div
            id="article-body"
            className="article-prose prose-drop mb-12 fade-up fade-up-2"
            dangerouslySetInnerHTML={{ __html: post.content }}
          />

          {/* Engagement row */}
          <div className="border-t border-border pt-8 mb-8">
            <div className="flex items-center gap-3">
              <LikeButton articleId={post.id} initialCount={post.likes_count} />
              <BookmarkButton articleId={post.id} />
              <div className="ml-auto">
                <ShareRow title={post.title} />
              </div>
            </div>
            <div className="mt-4">
              <WhoLiked articleId={post.id} />
            </div>
          </div>

          {/* Author card */}
          <div className="bg-surface border border-border rounded-2xl p-6 sm:p-8 mb-12 flex flex-col sm:flex-row items-start sm:items-center gap-5 shadow-soft">
            <Link href={`/profile/${username}`} className="shrink-0">
              <span className="w-16 h-16 rounded-full bg-accent-soft flex items-center justify-center text-2xl font-bold text-accent overflow-hidden block">
                {post.author?.avatar_url ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img src={post.author.avatar_url} alt={username} className="w-full h-full object-cover" />
                ) : (
                  username[0]?.toUpperCase()
                )}
              </span>
            </Link>
            <div className="flex-1 min-w-0">
              <p className="text-xs uppercase tracking-widest text-muted mb-1">Written by</p>
              <Link href={`/profile/${username}`} className="font-display text-xl text-ink hover:text-accent transition-colors inline-flex items-center gap-1.5">
                {username}
                {post.author?.is_verified && <VerifiedBadge />}
              </Link>
            </div>
            <FollowButton username={username} />
          </div>

          {/* More from this author */}
          {authorPosts.length > 0 && (
            <section className="mb-14">
              <h3 className="font-display text-2xl text-ink mb-6">
                More from <Link href={`/profile/${username}`} className="display-italic hover:underline">{username}</Link>
              </h3>
              <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {authorPosts.map((p) => <PostCard key={p.id} post={p} />)}
              </div>
            </section>
          )}

          {/* Comments */}
          <CommentSection articleId={post.id} />

          {/* Related */}
          {related.length > 0 && (
            <section className="mt-16">
              <h3 className="font-display text-2xl text-ink mb-6">
                Keep <span className="display-italic">reading</span>
              </h3>
              <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {related.map((p) => (
                  <PostCard key={p.id} post={p} />
                ))}
              </div>
            </section>
          )}
        </article>

        {/* Sticky table of contents (wide screens) */}
        <TableOfContents containerId="article-body" />
      </div>
    </>
  );
}
