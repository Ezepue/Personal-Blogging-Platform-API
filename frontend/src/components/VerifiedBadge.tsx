/** Verified-writer badge — a small checkmark shown beside verified authors. */
export default function VerifiedBadge({ className = "" }: { className?: string }) {
  return (
    <span title="Verified writer" aria-label="Verified writer" className={`inline-flex text-accent ${className}`}>
      <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" aria-hidden>
        <path d="M12 1.5l2.6 1.9 3.2-.2 1 3 2.7 1.7-1 3 1 3-2.7 1.7-1 3-3.2-.2L12 22.5l-2.6-1.9-3.2.2-1-3L2.5 16l1-3-1-3 2.7-1.7 1-3 3.2.2L12 1.5z" />
        <path d="M10.6 14.6l-2.2-2.2-1.4 1.4 3.6 3.6 6-6-1.4-1.4-4.6 4.6z" fill="var(--surface)" />
      </svg>
    </span>
  );
}
