import Link from "next/link";

export default function TagBadge({ tag }: { tag: string }) {
  return (
    <Link
      href={`/topics/${encodeURIComponent(tag)}`}
      className="text-xs px-2.5 py-1 rounded-full font-medium border border-border text-muted bg-raised hover:text-accent hover:border-accent transition-colors"
    >
      {tag}
    </Link>
  );
}
