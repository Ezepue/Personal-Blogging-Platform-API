import PostCard, { Post } from "@/components/PostCard";
import SearchBar from "@/components/SearchBar";

const API_URL = process.env.API_URL!;

async function getPosts(search?: string, category?: string): Promise<Post[]> {
  const params = new URLSearchParams();
  if (search) params.set("search", search);
  if (category) params.set("category", category);
  params.set("limit", "20");

  try {
    const res = await fetch(`${API_URL}/articles/?${params}`, {
      next: { revalidate: 60 },
    });
    if (!res.ok) return [];
    return res.json();
  } catch {
    return [];
  }
}

export default async function HomePage({
  searchParams,
}: {
  searchParams: { search?: string; category?: string };
}) {
  const posts = await getPosts(searchParams.search, searchParams.category);

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-[#f1f1f5] mb-2">Latest Posts</h1>
        <p className="text-muted">Discover stories, ideas, and expertise.</p>
      </div>

      {/* Search */}
      <SearchBar />

      {/* Active search indicator */}
      {searchParams.search && (
        <p className="text-sm text-muted mt-3">
          Showing results for &quot;{searchParams.search}&quot;
        </p>
      )}

      {/* Posts */}
      {posts.length === 0 ? (
        <div className="text-center py-20">
          <p className="text-muted text-lg">
            {searchParams.search ? "No posts match your search." : "No posts yet."}
          </p>
        </div>
      ) : (
        <div className="grid gap-4 mt-6">
          {posts.map((post) => (
            <PostCard key={post.id} post={post} />
          ))}
        </div>
      )}
    </div>
  );
}
