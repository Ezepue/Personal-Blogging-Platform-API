"use client";

import { useState, useRef, useEffect } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { useRouter } from "next/navigation";

export default function SettingsPage() {
  const { user, loading, refreshUser } = useAuth();
  const router = useRouter();

  const [username, setUsername] = useState("");
  const [bio, setBio] = useState("");
  const [profileMsg, setProfileMsg] = useState<{ text: string; ok: boolean } | null>(null);

  const [currentPw, setCurrentPw] = useState("");
  const [newPw, setNewPw] = useState("");
  const [confirmPw, setConfirmPw] = useState("");
  const [passwordMsg, setPasswordMsg] = useState<{ text: string; ok: boolean } | null>(null);

  const [savingProfile, setSavingProfile] = useState(false);
  const [savingPassword, setSavingPassword] = useState(false);

  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!loading && !user) router.push("/login");
  }, [user, loading, router]);

  // Populate form when user loads
  useEffect(() => {
    if (user) {
      setUsername(user.username);
      setBio(user.bio ?? "");
    }
  }, [user]);

  if (loading || !user) return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <div className="w-8 h-8 border-2 border-accent border-t-transparent rounded-full animate-spin" />
    </div>
  );

  const saveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setSavingProfile(true);
    setProfileMsg(null);
    try {
      const res = await fetch("/api/users/me", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: username.trim(), bio: bio.trim() }),
      });
      if (res.ok) {
        await refreshUser();
        setProfileMsg({ text: "Profile saved!", ok: true });
      } else {
        const err = await res.json().catch(() => ({})) as { detail?: string };
        setProfileMsg({ text: err.detail ?? "Failed to save profile", ok: false });
      }
    } finally {
      setSavingProfile(false);
    }
  };

  const changePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (newPw !== confirmPw) {
      setPasswordMsg({ text: "New passwords don't match", ok: false });
      return;
    }
    if (newPw.length < 8) {
      setPasswordMsg({ text: "Password must be at least 8 characters", ok: false });
      return;
    }
    setSavingPassword(true);
    setPasswordMsg(null);
    try {
      const res = await fetch("/api/users/me/password", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ current_password: currentPw, new_password: newPw }),
      });
      if (res.ok) {
        setPasswordMsg({ text: "Password updated successfully!", ok: true });
        setCurrentPw("");
        setNewPw("");
        setConfirmPw("");
      } else {
        const err = await res.json().catch(() => ({})) as { detail?: string };
        setPasswordMsg({ text: err.detail ?? "Failed to update password", ok: false });
      }
    } finally {
      setSavingPassword(false);
    }
  };

  const uploadAvatar = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    e.target.value = ""; // reset for re-upload
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch("/api/users/me/avatar", { method: "POST", body: formData });
    if (res.ok) await refreshUser();
  };

  const initials = user.username[0].toUpperCase();

  return (
    <div className="max-w-lg mx-auto space-y-8">
      <h1 className="text-2xl font-bold text-[#f1f1f5]">Settings</h1>

      {/* Avatar */}
      <div className="bg-surface border border-border rounded-xl p-6">
        <h2 className="font-semibold text-[#f1f1f5] mb-4">Avatar</h2>
        <div className="flex items-center gap-4">
          <button
            onClick={() => fileRef.current?.click()}
            className="w-16 h-16 rounded-full bg-accent/20 flex items-center justify-center text-2xl font-bold text-accent hover:bg-accent/30 transition-colors overflow-hidden flex-shrink-0"
          >
            {user.avatar_url ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img src={user.avatar_url} alt={user.username} className="w-full h-full object-cover" />
            ) : (
              initials
            )}
          </button>
          <div>
            <button
              onClick={() => fileRef.current?.click()}
              className="text-sm text-accent hover:underline block"
            >
              Upload photo
            </button>
            <p className="text-xs text-muted mt-0.5">JPG, PNG or WebP — max 10 MB</p>
          </div>
          <input ref={fileRef} type="file" accept="image/*" className="hidden" onChange={uploadAvatar} />
        </div>
      </div>

      {/* Profile */}
      <form onSubmit={saveProfile} className="bg-surface border border-border rounded-xl p-6 space-y-4">
        <h2 className="font-semibold text-[#f1f1f5]">Profile</h2>
        <div>
          <label className="block text-sm text-muted mb-1">Username</label>
          <input
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            className="w-full bg-hover border border-border rounded-lg px-4 py-2 text-[#f1f1f5] focus:outline-none focus:border-accent transition-colors"
          />
        </div>
        <div>
          <label className="block text-sm text-muted mb-1">Bio</label>
          <textarea
            value={bio}
            onChange={(e) => setBio(e.target.value)}
            rows={3}
            maxLength={160}
            className="w-full bg-hover border border-border rounded-lg px-4 py-2 text-[#f1f1f5] focus:outline-none focus:border-accent transition-colors resize-none"
          />
          <p className="text-xs text-muted mt-1">{bio.length}/160</p>
        </div>
        {profileMsg && (
          <p className={`text-sm ${profileMsg.ok ? "text-green-400" : "text-red-400"}`}>
            {profileMsg.text}
          </p>
        )}
        <button
          type="submit"
          disabled={savingProfile}
          className="bg-accent hover:bg-accent-hover text-white px-4 py-2 rounded-lg text-sm transition-colors disabled:opacity-50"
        >
          {savingProfile ? "Saving…" : "Save profile"}
        </button>
      </form>

      {/* Password */}
      <form onSubmit={changePassword} className="bg-surface border border-border rounded-xl p-6 space-y-4">
        <h2 className="font-semibold text-[#f1f1f5]">Change password</h2>
        <div>
          <label className="block text-sm text-muted mb-1">Current password</label>
          <input
            type="password"
            value={currentPw}
            onChange={(e) => setCurrentPw(e.target.value)}
            required
            className="w-full bg-hover border border-border rounded-lg px-4 py-2 text-[#f1f1f5] focus:outline-none focus:border-accent transition-colors"
          />
        </div>
        <div>
          <label className="block text-sm text-muted mb-1">New password</label>
          <input
            type="password"
            value={newPw}
            onChange={(e) => setNewPw(e.target.value)}
            required
            className="w-full bg-hover border border-border rounded-lg px-4 py-2 text-[#f1f1f5] focus:outline-none focus:border-accent transition-colors"
          />
        </div>
        <div>
          <label className="block text-sm text-muted mb-1">Confirm new password</label>
          <input
            type="password"
            value={confirmPw}
            onChange={(e) => setConfirmPw(e.target.value)}
            required
            className="w-full bg-hover border border-border rounded-lg px-4 py-2 text-[#f1f1f5] focus:outline-none focus:border-accent transition-colors"
          />
        </div>
        {passwordMsg && (
          <p className={`text-sm ${passwordMsg.ok ? "text-green-400" : "text-red-400"}`}>
            {passwordMsg.text}
          </p>
        )}
        <button
          type="submit"
          disabled={savingPassword}
          className="bg-accent hover:bg-accent-hover text-white px-4 py-2 rounded-lg text-sm transition-colors disabled:opacity-50"
        >
          {savingPassword ? "Updating…" : "Update password"}
        </button>
      </form>
    </div>
  );
}
