import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        base: "#0f0f13",
        surface: "#1a1a24",
        hover: "#22222e",
        border: "#2a2a38",
        accent: {
          DEFAULT: "#7c3aed",
          hover: "#6d28d9",
        },
        muted: "#8b8b9e",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [require("@tailwindcss/typography")],
};
export default config;
