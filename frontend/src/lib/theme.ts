/** Three-way theme control: light, dark, or follow-system. */

export type ThemePref = "light" | "dark" | "system";

const KEY = "quill-theme";

export function getThemePref(): ThemePref {
  if (typeof window === "undefined") return "system";
  const stored = localStorage.getItem(KEY);
  return stored === "light" || stored === "dark" ? stored : "system";
}

function resolve(pref: ThemePref): "light" | "dark" {
  if (pref === "system") {
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  return pref;
}

/** Persist a preference and apply the resolved theme to <html>. */
export function applyTheme(pref: ThemePref): void {
  if (typeof window === "undefined") return;
  if (pref === "system") localStorage.removeItem(KEY);
  else localStorage.setItem(KEY, pref);
  document.documentElement.setAttribute("data-theme", resolve(pref));
}
