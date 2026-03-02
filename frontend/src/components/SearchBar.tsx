"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useState, Suspense } from "react";

function SearchBarInner() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [query, setQuery] = useState(searchParams.get("search") ?? "");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const params = new URLSearchParams();
    if (query.trim()) params.set("search", query.trim());
    router.push(`/?${params.toString()}`);
  };

  const handleClear = () => {
    setQuery("");
    router.push("/");
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <div className="relative flex-1">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search posts..."
          className="w-full bg-surface border border-border rounded-lg px-4 py-2.5 text-[#f1f1f5] placeholder:text-muted focus:outline-none focus:border-accent transition-colors"
        />
        {query && (
          <button
            type="button"
            onClick={handleClear}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-muted hover:text-[#f1f1f5] text-lg leading-none"
            aria-label="Clear search"
          >
            ×
          </button>
        )}
      </div>
      <button
        type="submit"
        className="bg-accent hover:bg-accent-hover text-white px-5 py-2.5 rounded-lg transition-colors font-medium text-sm"
      >
        Search
      </button>
    </form>
  );
}

export default function SearchBar() {
  return (
    <Suspense fallback={<div className="h-11 bg-surface border border-border rounded-lg animate-pulse" />}>
      <SearchBarInner />
    </Suspense>
  );
}
