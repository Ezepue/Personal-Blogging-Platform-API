import PostCard, { Post } from "@/components/PostCard";
import SearchBar from "@/components/SearchBar";
import CategoryPills from "@/components/CategoryPills";

// Always render fresh — never serve stale cached data
export const dynamic = "force-dynamic";

const API_URL = process.env.API_URL ?? "http://localhost:8000";

async function getPosts(search?: string, category?: string): Promise<Post[]> {
  const params = new URLSearchParams();
  if (search) params.set("search", search);
  if (category) params.set("category", category);
  params.set("limit", "20");
  // No explicit status param — backend defaults to published only

  try {
    const res = await fetch(`${API_URL}/articles/?${params}`, {
      cache: "no-store", // always fetch fresh so router.refresh() works correctly
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
  searchParams: Promise<{ search?: string; category?: string }>;
}) {
  const { search, category } = await searchParams;
  const posts = await getPosts(search, category);

  // Derive unique categories from fetched posts for the pill filter
  const allCategories = Array.from(
    new Set(posts.map((p) => p.category).filter((c): c is string => !!c))
  ).sort();

  const isFiltering = !!search || !!category;

  return (
    <div>
      {/* Hero — only shown when not actively filtering */}
      {!isFiltering && (
        <div className="mb-10 py-8 border-b border-border">
          <p className="text-accent text-sm font-semibold tracking-wider uppercase mb-3">
            Welcome to Quill
          </p>
          <h1 className="text-4xl sm:text-5xl font-extrabold text-[#f1f1f5] mb-4 leading-tight">
            Stories worth reading.
          </h1>
          <p className="text-muted text-lg max-w-2xl leading-relaxed">
            Discover in-depth articles, tutorials, and ideas from writers across
            technology, design, science, and more.
          </p>
        </div>
      )}

      {/* Section heading when filtering */}
      {isFiltering && (
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-[#f1f1f5]">
            {search ? `Results for "${search}"` : `Category: ${category}`}
          </h1>
        </div>
      )}

      {/* Search */}
      <SearchBar />

      {/* Category pills */}
      <CategoryPills categories={allCategories} />

      {/* Post count hint */}
      <p className="text-xs text-muted mt-4 mb-2">
        {posts.length} {posts.length === 1 ? "post" : "posts"}
        {category ? ` in "${category}"` : ""}
        {search ? ` matching "${search}"` : ""}
      </p>

      {/* Posts */}
      {posts.length === 0 ? (
        <div className="text-center py-20">
          <p className="text-muted text-lg">
            {isFiltering ? "No posts match your filters." : "No posts published yet."}
          </p>
          {isFiltering && (
            <a href="/" className="text-accent hover:underline text-sm mt-3 inline-block">
              Clear filters
            </a>
          )}
        </div>
      ) : (
        <div className="grid gap-4 mt-2">
          {posts.map((post) => (
            <PostCard key={post.id} post={post} />
          ))}
        </div>
      )}
    </div>
  );
}
