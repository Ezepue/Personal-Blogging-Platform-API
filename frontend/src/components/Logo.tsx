import Link from "next/link";

/** Inline SVG pen-nib mark + wordmark. Works at any scale. */
export default function Logo({ className = "" }: { className?: string }) {
  return (
    <Link
      href="/"
      className={`inline-flex items-center gap-2 select-none group ${className}`}
      aria-label="Quill – home"
    >
      {/* Pen-nib icon */}
      <svg
        width="28"
        height="28"
        viewBox="0 0 28 28"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        aria-hidden="true"
      >
        {/* Background pill */}
        <rect width="28" height="28" rx="8" fill="#7c3aed" />

        {/* Nib body – a kite/diamond pointing down-right */}
        <path
          d="M7 7 L21 7 L21 17 L14 21 L7 17 Z"
          fill="white"
          fillOpacity="0.15"
        />

        {/* Nib tip – solid white triangle */}
        <path
          d="M14 21 L8 14 L14 11 L20 14 Z"
          fill="white"
          fillOpacity="0.9"
        />

        {/* Nib slit line */}
        <line
          x1="14"
          y1="11"
          x2="14"
          y2="21"
          stroke="#7c3aed"
          strokeWidth="1.2"
          strokeLinecap="round"
        />

        {/* Ink drop at the tip */}
        <circle cx="14" cy="21.5" r="1.2" fill="white" fillOpacity="0.85" />
      </svg>

      {/* Wordmark */}
      <span className="font-bold text-lg tracking-tight text-[#f1f1f5] group-hover:text-white transition-colors">
        Quill
      </span>
    </Link>
  );
}
