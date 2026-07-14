"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import PostCard, { Post } from "@/components/PostCard";

export default function BookmarksPage() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const [posts, setPosts] = useState<Post[]>([]);
  const [fetching, setFetching] = useState(true);

  useEffect(() => {
    if (!loading && !user) router.push("/login");
  }, [user, loading, router]);

  useEffect(() => {
    if (!user) return;
    fetch("/api/bookmarks/")
      .then((r) => (r.ok ? r.json() : []))
      .then((data) => setPosts(Array.isArray(data) ? data : []))
      .catch(() => {})
      .finally(() => setFetching(false));
  }, [user]);

  if (loading || !user) return null;

  return (
    <div className="max-w-4xl mx-auto">
      <p className="text-xs uppercase tracking-[0.3em] text-muted mb-3 fade-up">Your library</p>
      <h1 className="font-display text-5xl text-ink mb-10 fade-up">
        Reading <span className="display-italic">list</span>
      </h1>

      {fetching ? (
        <div className="flex items-center justify-center min-h-[30vh]">
          <div className="w-8 h-8 border-2 border-accent border-t-transparent rounded-full animate-spin" />
        </div>
      ) : posts.length === 0 ? (
        <div className="text-center py-20 fade-up">
          <p className="font-display text-2xl text-ink mb-2">Nothing saved yet</p>
          <p className="text-muted text-sm mb-6">
            Tap “Save” on any story to keep it here for later.
          </p>
          <Link
            href="/"
            className="inline-block bg-accent hover:bg-accent-hover text-white px-5 py-2.5 rounded-full text-sm font-medium transition-colors"
          >
            Explore stories
          </Link>
        </div>
      ) : (
        <div className="grid sm:grid-cols-2 gap-6 fade-up fade-up-1">
          {posts.map((post) => (
            <PostCard key={post.id} post={post} />
          ))}
        </div>
      )}
    </div>
  );
}
