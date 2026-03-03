"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { Suspense } from "react";

function Inner({ categories }: { categories: string[] }) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const current = searchParams.get("category") ?? "";
  const search = searchParams.get("search") ?? "";

  const navigate = (cat: string) => {
    const params = new URLSearchParams();
    if (search) params.set("search", search);
    if (cat) params.set("category", cat);
    router.push(`/?${params.toString()}`);
  };

  if (categories.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-2 mt-6">
      <button
        onClick={() => navigate("")}
        className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
          current === ""
            ? "bg-accent text-white"
            : "bg-surface border border-border text-muted hover:text-[#f1f1f5] hover:border-accent"
        }`}
      >
        All
      </button>
      {categories.map((cat) => (
        <button
          key={cat}
          onClick={() => navigate(cat)}
          className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
            current.toLowerCase() === cat.toLowerCase()
              ? "bg-accent text-white"
              : "bg-surface border border-border text-muted hover:text-[#f1f1f5] hover:border-accent"
          }`}
        >
          {cat}
        </button>
      ))}
    </div>
  );
}

export default function CategoryPills({ categories }: { categories: string[] }) {
  return (
    <Suspense fallback={<div className="h-9 mt-6" />}>
      <Inner categories={categories} />
    </Suspense>
  );
}
