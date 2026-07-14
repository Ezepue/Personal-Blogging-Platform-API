import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  darkMode: ["selector", '[data-theme="dark"]'],
  theme: {
    extend: {
      colors: {
        // All tokens resolve through CSS variables so the paper/ink themes
        // switch without any Tailwind dark: variants in markup.
        base: "var(--bg)",
        surface: "var(--surface)",
        raised: "var(--raised)",
        hover: "var(--raised)",
        border: "var(--border)",
        ink: {
          DEFAULT: "var(--ink)",
          soft: "var(--ink-soft)",
        },
        muted: "var(--muted)",
        accent: {
          DEFAULT: "var(--accent)",
          hover: "var(--accent-hover)",
          soft: "var(--accent-soft)",
        },
        accent2: {
          DEFAULT: "var(--accent2)",
          soft: "var(--accent2-soft)",
        },
        gold: "var(--gold)",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        display: [
          '"Iowan Old Style"',
          '"Palatino Linotype"',
          "Palatino",
          "Georgia",
          "serif",
        ],
      },
      boxShadow: {
        soft: "var(--shadow)",
        lift: "var(--shadow-lift)",
      },
    },
  },
  plugins: [require("@tailwindcss/typography")],
};
export default config;
