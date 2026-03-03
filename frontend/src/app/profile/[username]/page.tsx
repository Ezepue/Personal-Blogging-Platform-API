import { notFound } from "next/navigation";
import PostCard from "@/components/PostCard";
import type { Metadata } from "next";

const API_URL = process.env.API_URL ?? "http://localhost:8000";

type Profile = {
  id: number;
  username: string;
  bio: string | null;
  avatar_url: string | null;
  role: string;
};

async function getProfile(username: string): Promise<Profile | null> {
  const res = await fetch(`${API_URL}/users/${username}/profile`, {
    next: { revalidate: 60 },
  });
  if (!res.ok) return null;
  return res.json();
}

async function getUserPosts(username: string) {
  const res = await fetch(`${API_URL}/articles/?search=&limit=100&status=PUBLISHED`, {
    next: { revalidate: 60 },
  });
  if (!res.ok) return [];
  const all = await res.json();
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  return (Array.isArray(all) ? all : []).filter((p: any) => p.author?.username === username);
}

export async function generateMetadata(
  { params }: { params: Promise<{ username: string }> }
): Promise<Metadata> {
  const { username } = await params;
  const profile = await getProfile(username);
  if (!profile) return { title: "Profile not found" };
  return {
    title: `${profile.username} — Blog`,
    description: profile.bio ?? `Posts by ${profile.username}`,
  };
}

const roleBadge: Record<string, string> = {
  SUPER_ADMIN: "bg-red-900/50 text-red-300",
  ADMIN: "bg-orange-900/50 text-orange-300",
  AUTHOR: "bg-violet-900/50 text-violet-300",
  READER: "bg-gray-800 text-gray-300",
};

export default async function ProfilePage(
  { params }: { params: Promise<{ username: string }> }
) {
  const { username } = await params;

  const [profile, posts] = await Promise.all([
    getProfile(username),
    getUserPosts(username),
  ]);

  if (!profile) notFound();

  const badgeClass = roleBadge[profile.role] ?? "bg-gray-800 text-gray-300";

  return (
    <div className="max-w-3xl mx-auto">
      {/* Profile card */}
      <div className="bg-surface border border-border rounded-xl p-8 mb-8 flex gap-6 items-start">
        <div className="w-20 h-20 rounded-full bg-accent/20 flex items-center justify-center text-3xl font-bold text-accent flex-shrink-0 overflow-hidden">
          {profile.avatar_url ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={profile.avatar_url}
              alt={profile.username}
              className="w-full h-full object-cover"
            />
          ) : (
            profile.username[0].toUpperCase()
          )}
        </div>
        <div className="min-w-0">
          <div className="flex items-center gap-3 mb-1 flex-wrap">
            <h1 className="text-2xl font-bold text-[#f1f1f5]">{profile.username}</h1>
            <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${badgeClass}`}>
              {profile.role}
            </span>
          </div>
          {profile.bio && (
            <p className="text-muted mt-1 leading-relaxed">{profile.bio}</p>
          )}
          <p className="text-xs text-muted mt-2">
            {posts.length} {posts.length === 1 ? "post" : "posts"}
          </p>
        </div>
      </div>

      {/* Posts */}
      <h2 className="text-xl font-bold text-[#f1f1f5] mb-4">Posts</h2>
      {posts.length === 0 ? (
        <p className="text-muted text-center py-12">No published posts yet.</p>
      ) : (
        <div className="grid gap-4">
          {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
          {posts.map((post: any) => (
            <PostCard key={post.id} post={post} />
          ))}
        </div>
      )}
    </div>
  );
}
