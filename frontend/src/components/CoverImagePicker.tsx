"use client";

import { useRef, useState } from "react";

export default function CoverImagePicker({
  value,
  onChange,
}: {
  value: string;
  onChange: (url: string) => void;
}) {
  const fileRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  const upload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file) return;
    setUploading(true);
    setError("");
    try {
      const formData = new FormData();
      formData.append("file", file);
      const res = await fetch("/api/media/upload/", { method: "POST", body: formData });
      if (res.ok) {
        const data = await res.json();
        onChange(data.url as string);
      } else {
        setError("Upload failed — use JPG, PNG or GIF under 10 MB.");
      }
    } catch {
      setError("Upload failed. Check your connection.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="mb-4">
      {value ? (
        <div className="relative rounded-2xl overflow-hidden border border-border group">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={value} alt="Cover" className="w-full max-h-72 object-cover" />
          <div className="absolute top-3 right-3 flex gap-2">
            <button
              onClick={() => fileRef.current?.click()}
              className="bg-black/60 text-white text-xs px-3 py-1.5 rounded-full hover:bg-black/80 transition-colors"
            >
              Replace
            </button>
            <button
              onClick={() => onChange("")}
              className="bg-black/60 text-white text-xs px-3 py-1.5 rounded-full hover:bg-black/80 transition-colors"
            >
              Remove
            </button>
          </div>
        </div>
      ) : (
        <button
          onClick={() => fileRef.current?.click()}
          disabled={uploading}
          className="w-full border border-dashed border-border rounded-2xl py-6 text-sm text-muted hover:text-accent hover:border-accent transition-colors disabled:opacity-50"
        >
          {uploading ? "Uploading…" : "＋ Add a cover image"}
        </button>
      )}
      {error && <p className="text-red-400 text-xs mt-2">{error}</p>}
      <input ref={fileRef} type="file" accept="image/jpeg,image/png,image/gif" className="hidden" onChange={upload} />
    </div>
  );
}
