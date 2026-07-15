"use client";

import { useEffect, useState } from "react";

const SIZES = ["S", "M", "L"] as const;
type Size = (typeof SIZES)[number];
const FONT_PX: Record<Size, string> = { S: "1rem", M: "1.125rem", L: "1.3rem" };
const KEY = "quill-reader-size";

/**
 * Progressive enhancement for a rendered article body (by element id):
 * click-to-zoom images (lightbox), copy buttons on code blocks, and a
 * persisted reader text-size control.
 */
export default function ArticleEnhancer({ targetId }: { targetId: string }) {
  const [size, setSize] = useState<Size>("M");
  const [lightbox, setLightbox] = useState<string | null>(null);

  // Apply persisted reader size to the article body.
  useEffect(() => {
    const stored = (localStorage.getItem(KEY) as Size) || "M";
    setSize(SIZES.includes(stored) ? stored : "M");
  }, []);

  useEffect(() => {
    const el = document.getElementById(targetId);
    if (el) el.style.fontSize = FONT_PX[size];
  }, [size, targetId]);

  const choose = (s: Size) => {
    setSize(s);
    localStorage.setItem(KEY, s);
  };

  // Wire up image lightbox and code-copy buttons once the body is in the DOM.
  useEffect(() => {
    const container = document.getElementById(targetId);
    if (!container) return;

    const onImgClick = (e: Event) => {
      const img = e.target as HTMLImageElement;
      if (img.tagName === "IMG") setLightbox(img.src);
    };
    container.querySelectorAll("img").forEach((img) => {
      img.style.cursor = "zoom-in";
      img.addEventListener("click", onImgClick);
    });

    const cleanups: (() => void)[] = [];
    container.querySelectorAll("pre").forEach((pre) => {
      if (pre.querySelector(".code-copy")) return;
      const btn = document.createElement("button");
      btn.textContent = "Copy";
      btn.className = "code-copy";
      btn.style.cssText =
        "position:absolute;top:8px;right:8px;font-size:11px;padding:3px 8px;border-radius:6px;border:1px solid var(--border);background:var(--surface);color:var(--muted);cursor:pointer;";
      const onCopy = async () => {
        await navigator.clipboard.writeText(pre.innerText.replace(/\nCopy$/, ""));
        btn.textContent = "Copied";
        setTimeout(() => (btn.textContent = "Copy"), 1500);
      };
      btn.addEventListener("click", onCopy);
      pre.style.position = "relative";
      pre.appendChild(btn);
      cleanups.push(() => { btn.removeEventListener("click", onCopy); btn.remove(); });
    });

    return () => {
      container.querySelectorAll("img").forEach((img) => img.removeEventListener("click", onImgClick));
      cleanups.forEach((fn) => fn());
    };
  }, [targetId]);

  return (
    <>
      {/* Reader text-size control */}
      <div className="no-print flex items-center gap-1 border border-border rounded-full p-0.5" role="group" aria-label="Text size">
        {SIZES.map((s) => (
          <button
            key={s}
            onClick={() => choose(s)}
            aria-pressed={size === s}
            className={`w-7 h-7 rounded-full text-xs font-medium transition-colors ${
              size === s ? "bg-accent text-white" : "text-muted hover:text-ink"
            }`}
          >
            A{s === "S" ? "" : s === "L" ? "＋" : ""}
          </button>
        ))}
      </div>

      {lightbox && (
        <div
          className="fixed inset-0 z-[95] bg-black/85 flex items-center justify-center p-6 cursor-zoom-out"
          onClick={() => setLightbox(null)}
        >
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={lightbox} alt="" className="max-w-full max-h-full rounded-lg" />
        </div>
      )}
    </>
  );
}
