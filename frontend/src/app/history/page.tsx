"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import PostCard, { Post } from "@/components/PostCard";
import { useToast } from "@/components/ui/Toast";
import { useConfirm } from "@/components/ui/ConfirmDialog";
import { api } from "@/lib/api";

export default function HistoryPage() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const { toast } = useToast();
  const { confirm } = useConfirm();
  const [posts, setPosts] = useState<Post[]>([]);
  const [fetching, setFetching] = useState(true);

  useEffect(() => {
    if (!loading && !user) router.push("/login");
  }, [user, loading, router]);

  useEffect(() => {
    if (!user) return;
    api.get<Post[]>("/users/me/history")
      .then((data) => setPosts(Array.isArray(data) ? data : []))
      .catch(() => {})
      .finally(() => setFetching(false));
  }, [user]);

  const clear = async () => {
    if (!(await confirm({ title: "Clear reading history?", message: "This removes your recently viewed list. It can't be undone.", confirmLabel: "Clear", destructive: true }))) return;
    await api.del("/users/me/history");
    setPosts([]);
    toast("Reading history cleared", "success");
  };

  if (loading || !user) return null;

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-end justify-between mb-10">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-muted mb-3 fade-up">Recently read</p>
          <h1 className="font-display text-5xl text-ink fade-up">Reading <span className="display-italic">history</span></h1>
        </div>
        {posts.length > 0 && (
          <button onClick={clear} className="text-sm text-muted hover:text-red-500 transition-colors">Clear all</button>
        )}
      </div>

      {fetching ? (
        <div className="flex items-center justify-center min-h-[30vh]"><div className="w-8 h-8 border-2 border-accent border-t-transparent rounded-full animate-spin" /></div>
      ) : posts.length === 0 ? (
        <div className="text-center py-20 fade-up">
          <p className="font-display text-2xl text-ink mb-2">Nothing here yet</p>
          <p className="text-muted text-sm mb-6">Stories you read will show up here.</p>
          <Link href="/" className="inline-block bg-accent hover:bg-accent-hover text-white px-5 py-2.5 rounded-full text-sm font-medium transition-colors">Explore stories</Link>
        </div>
      ) : (
        <div className="grid sm:grid-cols-2 gap-6 fade-up fade-up-1">
          {posts.map((post) => <PostCard key={post.id} post={post} />)}
        </div>
      )}
    </div>
  );
}
