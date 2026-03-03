import { notFound } from "next/navigation";
import PostCard from "@/components/PostCard";
import ProfileDraftsTab from "@/components/ProfileDraftsTab";
import type { Metadata } from "next";

// Always render fresh — never serve stale cached data
export const dynamic = "force-dynamic";

const API_URL = process.env.API_URL ?? "http://localhost:8000";

type Profile = {
  id: number;
  username: string;
  bio: string | null;
  avatar_url: string | null;
  role: string;
};

async function getProfile(username: string): Promise<Profile | null> {
  try {
    const res = await fetch(`${API_URL}/users/${username}/profile`, {
      cache: "no-store",
    });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
async function getUserPosts(username: string): Promise<any[]> {
  try {
    const res = await fetch(`${API_URL}/users/${username}/articles?limit=100`, {
      cache: "no-store",
    });
    if (!res.ok) return [];
    return res.json();
  } catch {
    return [];
  }
}

export async function generateMetadata(
  { params }: { params: Promise<{ username: string }> }
): Promise<Metadata> {
  const { username } = await params;
  const profile = await getProfile(username);
  if (!profile) return { title: "Profile not found" };
  return {
    title: `${profile.username} — Quill`,
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

  // Stats derived from posts
  const totalLikes = posts.reduce(
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (sum: number, p: any) => sum + (p.likes_count ?? 0),
    0
  );
  const categories = Array.from(
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    new Set(posts.map((p: any) => p.category).filter(Boolean))
  ).length;

  return (
    <div className="max-w-3xl mx-auto">
      {/* Profile card */}
      <div className="bg-surface border border-border rounded-xl p-8 mb-8">
        <div className="flex gap-6 items-start mb-6">
          {/* Avatar */}
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

          {/* Name + bio */}
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-3 mb-1 flex-wrap">
              <h1 className="text-2xl font-bold text-[#f1f1f5]">{profile.username}</h1>
              <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${badgeClass}`}>
                {profile.role}
              </span>
            </div>
            {profile.bio && (
              <p className="text-muted mt-1 leading-relaxed text-sm">{profile.bio}</p>
            )}
          </div>
        </div>

        {/* Stats row */}
        <div className="grid grid-cols-3 gap-4 pt-5 border-t border-border">
          <div className="text-center">
            <p className="text-2xl font-bold text-[#f1f1f5]">{posts.length}</p>
            <p className="text-xs text-muted mt-0.5">{posts.length === 1 ? "Post" : "Posts"}</p>
          </div>
          <div className="text-center border-x border-border">
            <p className="text-2xl font-bold text-[#f1f1f5]">{totalLikes}</p>
            <p className="text-xs text-muted mt-0.5">Likes</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-[#f1f1f5]">{categories}</p>
            <p className="text-xs text-muted mt-0.5">{categories === 1 ? "Category" : "Categories"}</p>
          </div>
        </div>
      </div>

      {/* Tabs — ProfileDraftsTab is a client component that handles own-profile drafts tab */}
      <ProfileDraftsTab
        username={username}
        posts={posts}
        role={profile.role}
      />
    </div>
  );
}
