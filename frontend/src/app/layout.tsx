import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/contexts/AuthContext";
import { NotificationProvider } from "@/contexts/NotificationContext";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  // Absolute base for OG/Twitter images and canonical URLs. Set SITE_URL to the
  // public origin in production (e.g. https://blog.example.com); crawlers ignore
  // relative image URLs, so without this share previews would break.
  metadataBase: new URL(process.env.SITE_URL ?? "http://localhost:3000"),
  title: {
    default: "Quill — stories worth reading",
    template: "%s — Quill",
  },
  description: "An editorial home for essays, ideas, and stories worth reading.",
};

// Applied before hydration so the page never flashes the wrong theme.
const themeInit = `(function(){try{var t=localStorage.getItem("quill-theme");if(!t){t=window.matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light";}document.documentElement.setAttribute("data-theme",t);}catch(e){}})();`;

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeInit }} />
      </head>
      <body className={`${inter.className} min-h-screen flex flex-col`}>
        <AuthProvider>
          <NotificationProvider>
            <Navbar />
            <main className="relative z-10 flex-1 w-full max-w-6xl mx-auto px-4 sm:px-6 py-10">
              {children}
            </main>
            <Footer />
          </NotificationProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
