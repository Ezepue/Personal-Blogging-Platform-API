import SearchExperience from "@/components/SearchExperience";
import { Post } from "@/components/PostCard";
import type { Metadata } from "next";

const API_URL = process.env.API_URL ?? "http://localhost:8000";

export const metadata: Metadata = { title: "Search" };
export const dynamic = "force-dynamic";

type Author = { id: number; username: string; bio?: string | null; avatar_url?: string | null; is_verified?: boolean };

async function search(q: string): Promise<{ articles: Post[]; authors: Author[] }> {
  if (!q.trim()) return { articles: [], authors: [] };
  try {
    const res = await fetch(`${API_URL}/articles/search?q=${encodeURIComponent(q)}&limit=30`, {
      cache: "no-store",
    });
    return res.ok ? res.json() : { articles: [], authors: [] };
  } catch {
    return { articles: [], authors: [] };
  }
}

export default async function SearchPage({
  searchParams,
}: {
  searchParams: { q?: string };
}) {
  const q = searchParams.q ?? "";
  const { articles, authors } = await search(q);

  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="font-display text-4xl text-ink mb-8">
        Search the <span className="display-italic">archive</span>
      </h1>
      <SearchExperience query={q} articles={articles} authors={authors} />
    </div>
  );
}
