import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/contexts/AuthContext";
import { NotificationProvider } from "@/contexts/NotificationContext";
import Navbar from "@/components/Navbar";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Quill",
  description: "A personal blogging platform for stories worth reading.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} bg-base min-h-screen`}>
        <AuthProvider>
          <NotificationProvider>
            <Navbar />
            <main className="max-w-5xl mx-auto px-4 py-8">{children}</main>
          </NotificationProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
