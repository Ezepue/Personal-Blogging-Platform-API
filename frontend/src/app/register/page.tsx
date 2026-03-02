"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

type FormState = { username: string; email: string; password: string };

export default function RegisterPage() {
  const router = useRouter();
  const [form, setForm] = useState<FormState>({
    username: "",
    email: "",
    password: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await fetch("/api/users/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      if (res.ok) {
        router.push("/login?registered=1");
      } else {
        const err = await res.json().catch(() => ({ detail: "Registration failed" }));
        setError(err.detail ?? "Registration failed");
      }
    } catch {
      setError("Network error. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const fields: { key: keyof FormState; label: string; type: string; autoComplete: string }[] = [
    { key: "username", label: "Username", type: "text", autoComplete: "username" },
    { key: "email", label: "Email", type: "email", autoComplete: "email" },
    { key: "password", label: "Password", type: "password", autoComplete: "new-password" },
  ];

  return (
    <div className="max-w-sm mx-auto mt-16">
      <h1 className="text-3xl font-bold text-[#f1f1f5] mb-8 text-center">
        Create account
      </h1>

      <form onSubmit={handleSubmit} className="space-y-4">
        {fields.map(({ key, label, type, autoComplete }) => (
          <div key={key}>
            <label htmlFor={key} className="block text-sm text-muted mb-1.5">
              {label}
            </label>
            <input
              id={key}
              type={type}
              value={form[key]}
              onChange={(e) => setForm({ ...form, [key]: e.target.value })}
              required
              autoComplete={autoComplete}
              className="w-full bg-surface border border-border rounded-lg px-4 py-2.5 text-[#f1f1f5] focus:outline-none focus:border-accent transition-colors"
            />
          </div>
        ))}

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
          {loading ? "Creating account…" : "Create account"}
        </button>
      </form>

      <p className="text-center text-muted text-sm mt-6">
        Already have an account?{" "}
        <Link href="/login" className="text-accent hover:underline">
          Sign in
        </Link>
      </p>
    </div>
  );
}
