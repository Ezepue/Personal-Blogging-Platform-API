import Link from "next/link";

export default function NotFound() {
  return (
    <div className="text-center py-28">
      <p className="font-display text-7xl text-accent mb-4">404</p>
      <h1 className="font-display text-3xl text-ink mb-3">This page wandered off</h1>
      <p className="text-muted mb-8">The story you’re looking for may have been moved or unpublished.</p>
      <Link
        href="/"
        className="inline-block bg-accent hover:bg-accent-hover text-white px-6 py-3 rounded-full font-medium transition-colors"
      >
        Back to home
      </Link>
    </div>
  );
}
