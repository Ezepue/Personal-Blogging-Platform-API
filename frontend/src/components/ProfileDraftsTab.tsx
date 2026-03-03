"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import PostCard from "./PostCard";
import type { Post } from "./PostCard";

type Props = {
  username: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  posts: any[];
  role: string;
};

export default function ProfileDraftsTab({ username, posts, role }: Props) {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<"posts" | "drafts">("posts");
  const [drafts, setDrafts] = useState<Post[]>([]);
  const [draftsLoading, setDraftsLoading] = useState(false);
  const [isOwnProfile, setIsOwnProfile] = useState(false);
  const [publishing, setPublishing] = useState<number | null>(null);
  const [publishError, setPublishError] = useState("");

  // Determine if this is the logged-in user's own profile
  useEffect(() => {
    fetch("/api/users/me")
      .then((r) => (r.ok ? r.json() : null))
      .then((me) => {
        if (me?.username === username) setIsOwnProfile(true);
      })
      .catch(() => {});
  }, [username]);

  const canSeeDrafts =
    isOwnProfile &&
    (role === "AUTHOR" || role === "ADMIN" || role === "SUPER_ADMIN");

  // Fetch drafts when the tab is activated (or when canSeeDrafts first becomes true)
  useEffect(() => {
    if (activeTab !== "drafts" || !canSeeDrafts) return;
    setDraftsLoading(true);
    fetch("/api/articles/my-drafts")
      .then((r) => (r.ok ? r.json() : []))
      .then(setDrafts)
      .catch(() => setDrafts([]))
      .finally(() => setDraftsLoading(false));
  }, [activeTab, canSeeDrafts]);

  const publishDraft = async (id: number) => {
    setPublishing(id);
    setPublishError("");
    try {
      const res = await fetch(`/api/articles/${id}/publish`, { method: "PUT" });
      if (res.ok) {
        // Remove from drafts list immediately for instant feedback
        setDrafts((prev) => prev.filter((d) => d.id !== id));
        // Refresh server-component data so the Posts tab picks up the new article
        router.refresh();
      } else {
        const err = await res.json().catch(() => ({}));
        setPublishError((err as { detail?: string }).detail ?? "Failed to publish");
      }
    } finally {
      setPublishing(null);
    }
  };

  return (
    <div>
      {/* Tab bar */}
      <div className="flex gap-1 mb-6 border-b border-border">
        <button
          onClick={() => setActiveTab("posts")}
          className={`px-4 py-2.5 text-sm font-medium transition-colors border-b-2 -mb-px ${
            activeTab === "posts"
              ? "border-accent text-[#f1f1f5]"
              : "border-transparent text-muted hover:text-[#f1f1f5]"
          }`}
        >
          Posts
          <span className="ml-1.5 text-xs bg-surface border border-border rounded-full px-1.5 py-0.5">
            {posts.length}
          </span>
        </button>

        {canSeeDrafts && (
          <button
            onClick={() => setActiveTab("drafts")}
            className={`px-4 py-2.5 text-sm font-medium transition-colors border-b-2 -mb-px ${
              activeTab === "drafts"
                ? "border-accent text-[#f1f1f5]"
                : "border-transparent text-muted hover:text-[#f1f1f5]"
            }`}
          >
            Drafts
          </button>
        )}
      </div>

      {/* Posts tab */}
      {activeTab === "posts" && (
        <>
          {posts.length === 0 ? (
            <p className="text-muted text-center py-12">No published posts yet.</p>
          ) : (
            <div className="grid gap-4">
              {posts.map((post) => (
                <PostCard key={post.id} post={post} />
              ))}
            </div>
          )}
        </>
      )}

      {/* Drafts tab */}
      {activeTab === "drafts" && canSeeDrafts && (
        <>
          {publishError && (
            <p className="text-red-400 text-sm mb-4 bg-red-900/20 border border-red-900/30 rounded-lg px-4 py-2">
              {publishError}
            </p>
          )}

          {draftsLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="w-8 h-8 border-2 border-accent border-t-transparent rounded-full animate-spin" />
            </div>
          ) : drafts.length === 0 ? (
            <p className="text-muted text-center py-12">No drafts yet.</p>
          ) : (
            <div className="grid gap-4">
              {drafts.map((draft) => (
                <div key={draft.id} className="relative">
                  <PostCard post={draft} />
                  <div className="absolute top-4 right-4 flex gap-2">
                    <a
                      href={`/write/${draft.id}`}
                      className="text-xs bg-surface border border-border rounded-md px-2 py-1 text-muted hover:text-[#f1f1f5] hover:border-accent transition-colors"
                    >
                      Edit
                    </a>
                    <button
                      onClick={() => publishDraft(draft.id)}
                      disabled={publishing === draft.id}
                      className="text-xs bg-accent hover:bg-accent-hover text-white rounded-md px-2 py-1 transition-colors disabled:opacity-50"
                    >
                      {publishing === draft.id ? "…" : "Publish"}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
