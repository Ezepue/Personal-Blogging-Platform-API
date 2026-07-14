import PostCard, { Post } from "@/components/PostCard";
import type { Metadata } from "next";

const API_URL = process.env.API_URL ?? "http://localhost:8000";

export const revalidate = 120;

async function getPosts(tag: string): Promise<Post[]> {
  try {
    const res = await fetch(
      `${API_URL}/articles?tag=${encodeURIComponent(tag)}&limit=50`,
      { next: { revalidate: 120 } }
    );
    return res.ok ? res.json() : [];
  } catch {
    return [];
  }
}

export async function generateMetadata({
  params,
}: {
  params: { tag: string };
}): Promise<Metadata> {
  const tag = decodeURIComponent(params.tag);
  return { title: `#${tag}` };
}

export default async function TopicPage({
  params,
}: {
  params: { tag: string };
}) {
  const tag = decodeURIComponent(params.tag);
  const posts = await getPosts(tag);

  return (
    <div className="max-w-4xl mx-auto">
      <p className="text-xs uppercase tracking-[0.3em] text-muted mb-3 fade-up">Topic</p>
      <h1 className="font-display text-5xl text-ink mb-2 fade-up">
        <span className="display-italic">#</span>
        {tag}
      </h1>
      <p className="text-muted mb-10 fade-up fade-up-1">
        {posts.length} {posts.length === 1 ? "story" : "stories"}
      </p>

      {posts.length === 0 ? (
        <p className="text-muted text-center py-20">No stories under this topic yet.</p>
      ) : (
        <div className="grid sm:grid-cols-2 gap-6 fade-up fade-up-2">
          {posts.map((post) => (
            <PostCard key={post.id} post={post} />
          ))}
        </div>
      )}
    </div>
  );
}
