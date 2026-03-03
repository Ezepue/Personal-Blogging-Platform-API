"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";

export default function LoginPage() {
  const { login } = useAuth();
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(username, password);
      router.push("/");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-sm mx-auto mt-16">
      <h1 className="text-3xl font-bold text-[#f1f1f5] mb-8 text-center">
        Sign in
      </h1>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="username" className="block text-sm text-muted mb-1.5">
            Username
          </label>
          <input
            id="username"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            autoComplete="username"
            className="w-full bg-surface border border-border rounded-lg px-4 py-2.5 text-[#f1f1f5] focus:outline-none focus:border-accent transition-colors"
          />
        </div>

        <div>
          <label htmlFor="password" className="block text-sm text-muted mb-1.5">
            Password
          </label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            autoComplete="current-password"
            className="w-full bg-surface border border-border rounded-lg px-4 py-2.5 text-[#f1f1f5] focus:outline-none focus:border-accent transition-colors"
          />
        </div>

        {error && (
          <p role="alert" className="text-red-400 text-sm">
            {error}
          </p>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-accent hover:bg-accent-hover disabled:opacity-50 text-white py-2.5 rounded-lg font-medium transition-colors"
        >
          {loading ? "Signing in…" : "Sign in"}
        </button>
      </form>

      <p className="text-center text-muted text-sm mt-6">
        Don&apos;t have an account?{" "}
        <Link href="/register" className="text-accent hover:underline">
          Register
        </Link>
      </p>
    </div>
  );
}
