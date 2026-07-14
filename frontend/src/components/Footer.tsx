import Link from "next/link";

export default function Footer() {
  return (
    <footer className="relative z-10 border-t border-border mt-16">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-10 flex flex-col sm:flex-row items-center justify-between gap-4">
        <p className="font-display text-lg text-ink">
          Quill<span className="text-accent">.</span>
        </p>
        <nav className="flex items-center gap-6 text-sm text-muted">
          <Link href="/" className="link-flourish hover:text-ink transition-colors">Home</Link>
          <Link href="/topics" className="link-flourish hover:text-ink transition-colors">Topics</Link>
          <Link href="/search" className="link-flourish hover:text-ink transition-colors">Search</Link>
          <a href="/api/rss.xml" className="link-flourish hover:text-ink transition-colors">RSS</a>
        </nav>
        <p className="text-xs text-muted">Written with care. Published with Quill.</p>
      </div>
    </footer>
  );
}
