"use client";

import { useEffect, useState } from "react";
import { applyTheme, getThemePref, ThemePref } from "@/lib/theme";

const ORDER: ThemePref[] = ["light", "dark", "system"];
const LABEL: Record<ThemePref, string> = { light: "Light", dark: "Dark", system: "System" };

/** Cycles light → dark → follow-system. */
export default function ThemeToggle() {
  const [pref, setPref] = useState<ThemePref>("system");

  useEffect(() => setPref(getThemePref()), []);

  const cycle = () => {
    const next = ORDER[(ORDER.indexOf(pref) + 1) % ORDER.length];
    setPref(next);
    applyTheme(next);
  };

  return (
    <button
      onClick={cycle}
      aria-label={`Theme: ${LABEL[pref]}. Click to change.`}
      title={`Theme: ${LABEL[pref]}`}
      className="w-9 h-9 rounded-full border border-border text-muted hover:text-ink hover:border-ink transition-colors flex items-center justify-center"
    >
      {pref === "light" && (
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
          <circle cx="12" cy="12" r="4" />
          <path d="M12 2v2m0 16v2M4.9 4.9l1.4 1.4m11.4 11.4 1.4 1.4M2 12h2m16 0h2M4.9 19.1l1.4-1.4m11.4-11.4 1.4-1.4" />
        </svg>
      )}
      {pref === "dark" && (
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8Z" />
        </svg>
      )}
      {pref === "system" && (
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="2" y="3" width="20" height="14" rx="2" />
          <path d="M8 21h8m-4-4v4" />
        </svg>
      )}
    </button>
  );
}
