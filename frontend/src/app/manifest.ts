import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "Quill — Personal Blogging Platform",
    short_name: "Quill",
    description: "An editorial home for essays, ideas, and stories worth reading.",
    start_url: "/",
    display: "standalone",
    background_color: "#f7f3ec",
    theme_color: "#c2401d",
    icons: [
      {
        src:
          "data:image/svg+xml," +
          encodeURIComponent(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#c2401d"/><text x="50%" y="54%" font-family="Georgia,serif" font-size="42" fill="#fff" text-anchor="middle" dominant-baseline="middle">Q</text></svg>',
          ),
        sizes: "any",
        type: "image/svg+xml",
      },
    ],
  };
}
