"use client";

export default function Error({ reset }: { error: Error; reset: () => void }) {
  return (
    <div className="text-center py-28">
      <p className="font-display text-6xl text-accent mb-4">Oh no</p>
      <h1 className="font-display text-3xl text-ink mb-3">Something went wrong</h1>
      <p className="text-muted mb-8">An unexpected error interrupted this page.</p>
      <button
        onClick={reset}
        className="inline-block bg-accent hover:bg-accent-hover text-white px-6 py-3 rounded-full font-medium transition-colors"
      >
        Try again
      </button>
    </div>
  );
}
