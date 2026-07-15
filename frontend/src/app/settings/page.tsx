"use client";

import { useState, useRef, useEffect } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { useRouter } from "next/navigation";
import { useToast } from "@/components/ui/Toast";
import { useConfirm } from "@/components/ui/ConfirmDialog";
import { formatDate } from "@/lib/format";
import { api } from "@/lib/api";

type Prefs = { notify_likes: boolean; notify_comments: boolean; notify_follows: boolean };
type Session = { id: number; created_at: string; expires_at: string };

function SecuritySections() {
  const { logout } = useAuth();
  const { toast } = useToast();
  const { confirm } = useConfirm();
  const [sessions, setSessions] = useState<Session[]>([]);
  const [deletePw, setDeletePw] = useState("");

  useEffect(() => {
    api.get<Session[]>("/users/me/sessions").then(setSessions).catch(() => {});
  }, []);

  const revoke = async (id: number) => {
    if (!(await confirm({ title: "Revoke this session?", message: "That device will be signed out.", confirmLabel: "Revoke", destructive: true }))) return;
    await api.del(`/users/me/sessions/${id}`);
    setSessions((s) => s.filter((x) => x.id !== id));
    toast("Session revoked", "success");
  };

  const exportData = async () => {
    const data = await api.get<unknown>("/users/me/export");
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "quill-export.json";
    a.click();
    URL.revokeObjectURL(url);
    toast("Your data is downloading", "success");
  };

  const deleteAccount = async () => {
    if (!deletePw) return;
    if (!(await confirm({ title: "Delete your account?", message: "Your stories and comments will be hidden and you'll be signed out. This can't be undone.", confirmLabel: "Delete account", destructive: true }))) return;
    try {
      await api.del("/users/me", { password: deletePw });
      toast("Account deleted", "success");
      logout();
    } catch {
      toast("Password is incorrect", "error");
    }
  };

  return (
    <>
      <div className="bg-surface border border-border rounded-2xl p-6 shadow-soft">
        <h2 className="font-semibold text-ink mb-1">Active sessions</h2>
        <p className="text-xs text-muted mb-4">Devices currently signed in to your account.</p>
        <div className="space-y-2">
          {sessions.length === 0 && <p className="text-sm text-muted">No active sessions.</p>}
          {sessions.map((s) => (
            <div key={s.id} className="flex items-center justify-between text-sm border border-border rounded-lg px-4 py-2.5">
              <span className="text-ink-soft">Session #{s.id} · started {formatDate(s.created_at)}</span>
              <button onClick={() => revoke(s.id)} className="text-muted hover:text-red-500 transition-colors">Revoke</button>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-surface border border-border rounded-2xl p-6 shadow-soft">
        <h2 className="font-semibold text-ink mb-1">Your data</h2>
        <p className="text-xs text-muted mb-4">Download a JSON copy of your profile, stories, and comments.</p>
        <button onClick={exportData} className="px-5 py-2 rounded-full border border-border text-ink-soft hover:text-ink hover:border-ink text-sm transition-colors">
          Export my data
        </button>
      </div>

      <div className="bg-surface border border-red-500/40 rounded-2xl p-6 shadow-soft">
        <h2 className="font-semibold text-red-500 mb-1">Danger zone</h2>
        <p className="text-xs text-muted mb-4">Deleting your account hides your content and signs you out. Confirm with your password.</p>
        <div className="flex flex-col sm:flex-row gap-3">
          <input
            type="password"
            value={deletePw}
            onChange={(e) => setDeletePw(e.target.value)}
            placeholder="Your password"
            className="flex-1 bg-raised border border-border rounded-lg px-4 py-2 text-ink focus:outline-none focus:border-red-500 transition-colors"
          />
          <button
            onClick={deleteAccount}
            disabled={!deletePw}
            className="px-5 py-2 rounded-full bg-red-600 hover:bg-red-700 disabled:opacity-40 text-white text-sm font-medium transition-colors"
          >
            Delete account
          </button>
        </div>
      </div>
    </>
  );
}

const inputCls =
  "w-full bg-raised border border-border rounded-lg px-4 py-2 text-ink focus:outline-none focus:border-accent transition-colors";

export default function SettingsPage() {
  const { user, loading, refreshUser } = useAuth();
  const router = useRouter();

  const [username, setUsername] = useState("");
  const [bio, setBio] = useState("");
  const [website, setWebsite] = useState("");
  const [location, setLocation] = useState("");
  const [twitter, setTwitter] = useState("");
  const [github, setGithub] = useState("");
  const [profileMsg, setProfileMsg] = useState<{ text: string; ok: boolean } | null>(null);

  const [prefs, setPrefs] = useState<Prefs>({
    notify_likes: true,
    notify_comments: true,
    notify_follows: true,
  });
  const [prefsMsg, setPrefsMsg] = useState<string>("");

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

  // Populate forms when user loads
  useEffect(() => {
    if (!user) return;
    setUsername(user.username);
    setBio(user.bio ?? "");
    fetch(`/api/users/${user.username}/profile`)
      .then((r) => (r.ok ? r.json() : null))
      .then((p) => {
        if (!p) return;
        setWebsite(p.website ?? "");
        setLocation(p.location ?? "");
        setTwitter(p.twitter ?? "");
        setGithub(p.github ?? "");
      })
      .catch(() => {});
    fetch("/api/users/me/notification-prefs")
      .then((r) => (r.ok ? r.json() : null))
      .then((p) => p && setPrefs(p))
      .catch(() => {});
  }, [user]);

  if (loading || !user)
    return (
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
        body: JSON.stringify({
          username: username.trim(),
          bio: bio.trim(),
          website: website.trim() || null,
          location: location.trim() || null,
          twitter: twitter.trim().replace(/^@/, "") || null,
          github: github.trim() || null,
        }),
      });
      if (res.ok) {
        await refreshUser();
        setProfileMsg({ text: "Profile saved!", ok: true });
      } else {
        const err = (await res.json().catch(() => ({}))) as { detail?: string };
        setProfileMsg({ text: err.detail ?? "Failed to save profile", ok: false });
      }
    } finally {
      setSavingProfile(false);
    }
  };

  const savePrefs = async (next: Prefs) => {
    setPrefs(next); // optimistic
    setPrefsMsg("");
    const res = await fetch("/api/users/me/notification-prefs", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(next),
    });
    if (res.ok) {
      setPrefsMsg("Saved");
      setTimeout(() => setPrefsMsg(""), 1500);
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
        const err = (await res.json().catch(() => ({}))) as { detail?: string };
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

  const removeAvatar = async () => {
    const res = await fetch("/api/users/me/avatar", { method: "DELETE" });
    if (res.ok) await refreshUser();
  };

  const initials = user.username[0].toUpperCase();

  const prefRows: { key: keyof Prefs; label: string; hint: string }[] = [
    { key: "notify_likes", label: "Likes", hint: "When someone likes your story" },
    { key: "notify_comments", label: "Comments & replies", hint: "When someone comments on your story or replies to you" },
    { key: "notify_follows", label: "New followers", hint: "When someone starts following you" },
  ];

  return (
    <div className="max-w-lg mx-auto space-y-8">
      <h1 className="font-display text-4xl text-ink">Settings</h1>

      {/* Avatar */}
      <div className="bg-surface border border-border rounded-2xl p-6 shadow-soft">
        <h2 className="font-semibold text-ink mb-4">Avatar</h2>
        <div className="flex items-center gap-4">
          <button
            onClick={() => fileRef.current?.click()}
            className="w-16 h-16 rounded-full bg-accent-soft flex items-center justify-center text-2xl font-bold text-accent transition-colors overflow-hidden flex-shrink-0"
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
            {user.avatar_url && (
              <button onClick={removeAvatar} className="text-sm text-muted hover:text-red-500 transition-colors block mt-0.5">
                Remove photo
              </button>
            )}
            <p className="text-xs text-muted mt-0.5">JPG, PNG or WebP — max 10 MB</p>
          </div>
          <input ref={fileRef} type="file" accept="image/*" className="hidden" onChange={uploadAvatar} />
        </div>
      </div>

      {/* Profile */}
      <form onSubmit={saveProfile} className="bg-surface border border-border rounded-2xl p-6 space-y-4 shadow-soft">
        <h2 className="font-semibold text-ink">Public profile</h2>
        <div>
          <label className="block text-sm text-muted mb-1">Username</label>
          <input value={username} onChange={(e) => setUsername(e.target.value)} required className={inputCls} />
        </div>
        <div>
          <label className="block text-sm text-muted mb-1">Bio</label>
          <textarea
            value={bio}
            onChange={(e) => setBio(e.target.value)}
            rows={3}
            maxLength={160}
            className={`${inputCls} resize-none`}
          />
          <p className="text-xs text-muted mt-1">{bio.length}/160</p>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-muted mb-1">Website</label>
            <input value={website} onChange={(e) => setWebsite(e.target.value)} placeholder="example.com" className={inputCls} />
          </div>
          <div>
            <label className="block text-sm text-muted mb-1">Location</label>
            <input value={location} onChange={(e) => setLocation(e.target.value)} placeholder="Lagos, Nigeria" className={inputCls} />
          </div>
          <div>
            <label className="block text-sm text-muted mb-1">X / Twitter</label>
            <input value={twitter} onChange={(e) => setTwitter(e.target.value)} placeholder="@handle" className={inputCls} />
          </div>
          <div>
            <label className="block text-sm text-muted mb-1">GitHub</label>
            <input value={github} onChange={(e) => setGithub(e.target.value)} placeholder="username" className={inputCls} />
          </div>
        </div>
        {profileMsg && (
          <p className={`text-sm ${profileMsg.ok ? "text-green-500" : "text-red-400"}`}>{profileMsg.text}</p>
        )}
        <button
          type="submit"
          disabled={savingProfile}
          className="bg-accent hover:bg-accent-hover text-white px-5 py-2 rounded-full text-sm font-medium transition-colors disabled:opacity-50"
        >
          {savingProfile ? "Saving…" : "Save profile"}
        </button>
      </form>

      {/* Notification preferences */}
      <div className="bg-surface border border-border rounded-2xl p-6 shadow-soft">
        <div className="flex items-center justify-between mb-1">
          <h2 className="font-semibold text-ink">Notifications</h2>
          {prefsMsg && <span className="text-xs text-green-500">{prefsMsg}</span>}
        </div>
        <p className="text-xs text-muted mb-4">Choose what you want to hear about.</p>
        <div className="space-y-3">
          {prefRows.map((row) => (
            <label key={row.key} className="flex items-start justify-between gap-4 cursor-pointer group">
              <span>
                <span className="block text-sm text-ink group-hover:text-accent transition-colors">{row.label}</span>
                <span className="block text-xs text-muted">{row.hint}</span>
              </span>
              <input
                type="checkbox"
                checked={prefs[row.key]}
                onChange={(e) => savePrefs({ ...prefs, [row.key]: e.target.checked })}
                className="mt-1 w-4 h-4 accent-[var(--accent)]"
              />
            </label>
          ))}
        </div>
      </div>

      {/* Password */}
      <form onSubmit={changePassword} className="bg-surface border border-border rounded-2xl p-6 space-y-4 shadow-soft">
        <h2 className="font-semibold text-ink">Change password</h2>
        <div>
          <label className="block text-sm text-muted mb-1">Current password</label>
          <input type="password" value={currentPw} onChange={(e) => setCurrentPw(e.target.value)} required className={inputCls} />
        </div>
        <div>
          <label className="block text-sm text-muted mb-1">New password</label>
          <input type="password" value={newPw} onChange={(e) => setNewPw(e.target.value)} required className={inputCls} />
        </div>
        <div>
          <label className="block text-sm text-muted mb-1">Confirm new password</label>
          <input type="password" value={confirmPw} onChange={(e) => setConfirmPw(e.target.value)} required className={inputCls} />
        </div>
        {passwordMsg && (
          <p className={`text-sm ${passwordMsg.ok ? "text-green-500" : "text-red-400"}`}>{passwordMsg.text}</p>
        )}
        <button
          type="submit"
          disabled={savingPassword}
          className="bg-accent hover:bg-accent-hover text-white px-5 py-2 rounded-full text-sm font-medium transition-colors disabled:opacity-50"
        >
          {savingPassword ? "Updating…" : "Update password"}
        </button>
      </form>

      <SecuritySections />
    </div>
  );
}
