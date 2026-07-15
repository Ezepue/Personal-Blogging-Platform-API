"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { errorMessage } from "@/lib/api";

type FormState = { username: string; email: string; password: string };

function passwordStrength(pw: string): { score: number; label: string } {
  let score = 0;
  if (pw.length >= 8) score++;
  if (pw.length >= 12) score++;
  if (/[A-Z]/.test(pw) && /[a-z]/.test(pw)) score++;
  if (/\d/.test(pw)) score++;
  if (/[^A-Za-z0-9]/.test(pw)) score++;
  const label = ["Too short", "Weak", "Fair", "Good", "Strong", "Excellent"][score];
  return { score, label };
}

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
        const err = await res.json().catch(() => null);
        setError(errorMessage(err, "Registration failed"));
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
      <h1 className="text-3xl font-bold text-ink mb-8 text-center">
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
              className="w-full bg-surface border border-border rounded-lg px-4 py-2.5 text-ink focus:outline-none focus:border-accent transition-colors"
            />
            {key === "password" && form.password.length > 0 && (
              <div className="mt-2 flex items-center gap-2">
                <div className="flex-1 h-1 rounded-full bg-border overflow-hidden">
                  <div
                    className="h-full transition-all"
                    style={{
                      width: `${(passwordStrength(form.password).score / 5) * 100}%`,
                      backgroundColor:
                        passwordStrength(form.password).score <= 1
                          ? "#ef4444"
                          : passwordStrength(form.password).score <= 3
                          ? "var(--gold)"
                          : "#22c55e",
                    }}
                  />
                </div>
                <span className="text-xs text-muted w-16 text-right">
                  {passwordStrength(form.password).label}
                </span>
              </div>
            )}
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
