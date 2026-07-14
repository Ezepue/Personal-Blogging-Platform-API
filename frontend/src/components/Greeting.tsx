"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/contexts/AuthContext";

/** Time-of-day greeting for signed-in readers; renders nothing when logged out. */
export default function Greeting() {
  const { user } = useAuth();
  const [part, setPart] = useState("");

  useEffect(() => {
    const h = new Date().getHours();
    setPart(h < 12 ? "morning" : h < 18 ? "afternoon" : "evening");
  }, []);

  if (!user || !part) return null;

  return (
    <p className="text-sm text-muted mb-2 fade-up">
      Good {part}, <span className="text-ink font-medium">{user.username}</span> — here’s what’s new.
    </p>
  );
}
