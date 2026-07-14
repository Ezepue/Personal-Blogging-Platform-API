"use client";

import { useState } from "react";

export default function ShareRow({ title }: { title: string }) {
  const [copied, setCopied] = useState(false);

  const pageUrl = () => (typeof window !== "undefined" ? window.location.href : "");

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(pageUrl());
      setCopied(true);
      setTimeout(() => setCopied(false), 1800);
    } catch {
      // clipboard unavailable — ignore
    }
  };

  const shareX = () => {
    const u = new URL("https://twitter.com/intent/tweet");
    u.searchParams.set("text", title);
    u.searchParams.set("url", pageUrl());
    window.open(u.toString(), "_blank", "noopener");
  };

  const shareLinkedIn = () => {
    const u = new URL("https://www.linkedin.com/sharing/share-offsite/");
    u.searchParams.set("url", pageUrl());
    window.open(u.toString(), "_blank", "noopener");
  };

  const btn =
    "w-9 h-9 rounded-full border border-border text-muted hover:text-ink hover:border-ink transition-colors flex items-center justify-center";

  return (
    <div className="flex items-center gap-2">
      <button onClick={copy} className={btn} aria-label="Copy link" title={copied ? "Copied!" : "Copy link"}>
        {copied ? (
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M20 6 9 17l-5-5" />
          </svg>
        ) : (
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <path d="M10 13a5 5 0 0 0 7.5.5l3-3a5 5 0 0 0-7-7l-1.7 1.7" />
            <path d="M14 11a5 5 0 0 0-7.5-.5l-3 3a5 5 0 0 0 7 7l1.7-1.7" />
          </svg>
        )}
      </button>
      <button onClick={shareX} className={btn} aria-label="Share on X" title="Share on X">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor">
          <path d="M18.9 1.2h3.7l-8.1 9.3L24 22.8h-7.5l-5.9-7.7-6.7 7.7H.2l8.7-9.9L0 1.2h7.7l5.3 7 6-7Zm-1.3 19.4h2L7.1 3.3H4.9l12.7 17.3Z" />
        </svg>
      </button>
      <button onClick={shareLinkedIn} className={btn} aria-label="Share on LinkedIn" title="Share on LinkedIn">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
          <path d="M20.4 20.4h-3.5v-5.6c0-1.3 0-3-1.9-3s-2.1 1.4-2.1 2.9v5.7H9.4V9h3.4v1.6h.1a3.7 3.7 0 0 1 3.3-1.8c3.6 0 4.2 2.3 4.2 5.4v6.2ZM5.3 7.4a2 2 0 1 1 0-4.1 2 2 0 0 1 0 4.1ZM7.1 20.4H3.6V9h3.5v11.4Z" />
        </svg>
      </button>
    </div>
  );
}
