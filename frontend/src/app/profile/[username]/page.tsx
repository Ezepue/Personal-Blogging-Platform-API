import { notFound } from "next/navigation";
import ProfileDraftsTab from "@/components/ProfileDraftsTab";
import FollowButton from "@/components/FollowButton";
import type { Metadata } from "next";

const API_URL = process.env.API_URL ?? "http://localhost:8000";

type Profile = {
  id: number;
  username: string;
  bio: string | null;
  avatar_url: string | null;
  role: string;
  website?: string | null;
  location?: string | null;
  twitter?: string | null;
  github?: string | null;
  created_at?: string | null;
  followers_count: number;
  following_count: number;
  articles_count: number;
};

async function getProfile(username: string): Promise<Profile | null> {
  const res = await fetch(`${API_URL}/users/${username}/profile`, {
    next: { revalidate: 60 },
  });
  if (!res.ok) return null;
  return res.json();
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
async function getUserPosts(username: string): Promise<any[]> {
  const res = await fetch(`${API_URL}/users/${username}/articles?limit=100`, {
    next: { revalidate: 60 },
  });
  if (!res.ok) return [];
  return res.json();
}

export async function generateMetadata({
  params,
}: {
  params: { username: string };
}): Promise<Metadata> {
  const profile = await getProfile(params.username);
  if (!profile) return { title: "Profile not found" };
  return {
    title: profile.username,
    description: profile.bio ?? `Stories by ${profile.username}`,
  };
}

export default async function ProfilePage({
  params,
}: {
  params: { username: string };
}) {
  const { username } = params;
  const [profile, posts] = await Promise.all([getProfile(username), getUserPosts(username)]);
  if (!profile) notFound();

  const joined = profile.created_at
    ? new Date(profile.created_at).toLocaleDateString("en-US", { month: "long", year: "numeric" })
    : null;

  const links = [
    profile.website && {
      href: profile.website.startsWith("http") ? profile.website : `https://${profile.website}`,
      label: profile.website.replace(/^https?:\/\//, ""),
    },
    profile.twitter && { href: `https://x.com/${profile.twitter}`, label: `@${profile.twitter}` },
    profile.github && { href: `https://github.com/${profile.github}`, label: `github/${profile.github}` },
  ].filter(Boolean) as { href: string; label: string }[];

  return (
    <div className="max-w-3xl mx-auto">
      {/* Banner */}
      <div className="relative h-36 sm:h-44 -mx-4 sm:mx-0 sm:rounded-3xl overflow-hidden mb-0 fade-up">
        <div
          className="absolute inset-0"
          style={{
            background:
              "linear-gradient(120deg, var(--accent-soft), var(--accent2-soft) 55%, transparent), var(--raised)",
          }}
        />
        <div className="art-field" aria-hidden />
      </div>

      {/* Profile header */}
      <div className="relative px-2 sm:px-8 -mt-12 mb-10 fade-up fade-up-1">
        <div className="flex items-end justify-between mb-4">
          <div className="w-24 h-24 rounded-full border-4 border-base bg-accent-soft flex items-center justify-center text-4xl font-bold text-accent overflow-hidden shadow-soft">
            {profile.avatar_url ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img src={profile.avatar_url} alt={profile.username} className="w-full h-full object-cover" />
            ) : (
              profile.username[0].toUpperCase()
            )}
          </div>
          <FollowButton username={profile.username} />
        </div>

        <h1 className="font-display text-4xl text-ink mb-1">{profile.username}</h1>
        {profile.bio && <p className="text-ink-soft leading-relaxed max-w-xl mb-3">{profile.bio}</p>}

        {/* Meta line: location, joined, links */}
        <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-muted mb-5">
          {profile.location && <span>📍 {profile.location}</span>}
          {joined && <span>Joined {joined}</span>}
          {links.map((l) => (
            <a
              key={l.href}
              href={l.href}
              target="_blank"
              rel="noopener noreferrer"
              className="text-accent hover:underline"
            >
              {l.label}
            </a>
          ))}
        </div>

        {/* Stats */}
        <div className="flex items-center gap-6 text-sm">
          <span className="text-ink font-semibold">
            {profile.articles_count}
            <span className="text-muted font-normal"> {profile.articles_count === 1 ? "story" : "stories"}</span>
          </span>
          <span className="text-ink font-semibold">
            {profile.followers_count}
            <span className="text-muted font-normal"> followers</span>
          </span>
          <span className="text-ink font-semibold">
            {profile.following_count}
            <span className="text-muted font-normal"> following</span>
          </span>
        </div>
      </div>

      {/* Posts / drafts tabs */}
      <div className="fade-up fade-up-2">
        <ProfileDraftsTab username={username} posts={posts} role={profile.role} />
      </div>
    </div>
  );
}
