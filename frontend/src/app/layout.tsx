import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Providers from "@/components/Providers";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import BackToTop from "@/components/BackToTop";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  metadataBase: new URL(process.env.SITE_URL ?? "http://localhost:3000"),
  title: {
    default: "Quill — stories worth reading",
    template: "%s — Quill",
  },
  description: "An editorial home for essays, ideas, and stories worth reading.",
  manifest: "/manifest.webmanifest",
};

// Applied before hydration so the page never flashes the wrong theme.
const themeInit = `(function(){try{var t=localStorage.getItem("quill-theme");if(t!=="light"&&t!=="dark"){t=window.matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light";}document.documentElement.setAttribute("data-theme",t);}catch(e){}})();`;

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeInit }} />
      </head>
      <body className={`${inter.className} min-h-screen flex flex-col`}>
        <a
          href="#main"
          className="sr-only focus:not-sr-only focus:fixed focus:top-3 focus:left-3 focus:z-[100] focus:bg-accent focus:text-white focus:px-4 focus:py-2 focus:rounded-full"
        >
          Skip to content
        </a>
        <Providers>
          <Navbar />
          <main id="main" className="relative z-10 flex-1 w-full max-w-6xl mx-auto px-4 sm:px-6 py-10">
            {children}
          </main>
          <Footer />
          <BackToTop />
        </Providers>
      </body>
    </html>
  );
}
