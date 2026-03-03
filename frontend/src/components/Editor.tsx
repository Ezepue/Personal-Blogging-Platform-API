"use client";

import { useEditor, EditorContent } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import Image from "@tiptap/extension-image";
import Placeholder from "@tiptap/extension-placeholder";
import CodeBlockLowlight from "@tiptap/extension-code-block-lowlight";
import { common, createLowlight } from "lowlight";
import { useRef } from "react";

const lowlight = createLowlight(common);

type EditorProps = {
  content: string;
  onChange: (html: string) => void;
};

export default function Editor({ content, onChange }: EditorProps) {
  const editor = useEditor({
    immediatelyRender: false,
    extensions: [
      StarterKit.configure({ codeBlock: false }),
      CodeBlockLowlight.configure({ lowlight }),
      Image,
      Placeholder.configure({ placeholder: "Start writing…" }),
    ],
    content,
    onUpdate: ({ editor }) => onChange(editor.getHTML()),
  });

  const fileRef = useRef<HTMLInputElement>(null);

  const uploadImage = async (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await fetch("/api/media/upload/", { method: "POST", body: formData });
      if (res.ok) {
        const data = await res.json();
        editor?.chain().focus().setImage({ src: `/api/media/${data.filename}` }).run();
      } else {
        console.error("Image upload failed:", res.status);
      }
    } catch (err) {
      console.error("Image upload error:", err);
    }
  };

  if (!editor) return null;

  const btn = (label: string, action: () => boolean, active?: boolean) => (
    <button
      type="button"
      onClick={() => action()}
      className={`px-2 py-1 rounded text-sm transition-colors ${
        active ? "bg-accent text-white" : "text-muted hover:text-[#f1f1f5] hover:bg-hover"
      }`}
    >
      {label}
    </button>
  );

  return (
    <div className="bg-surface border border-border rounded-xl overflow-hidden">
      {/* Toolbar */}
      <div className="border-b border-border px-3 py-2 flex flex-wrap gap-1 items-center">
        {btn("B", () => editor.chain().focus().toggleBold().run(), editor.isActive("bold"))}
        {btn("I", () => editor.chain().focus().toggleItalic().run(), editor.isActive("italic"))}
        {btn("H1", () => editor.chain().focus().toggleHeading({ level: 1 }).run(), editor.isActive("heading", { level: 1 }))}
        {btn("H2", () => editor.chain().focus().toggleHeading({ level: 2 }).run(), editor.isActive("heading", { level: 2 }))}
        {btn("H3", () => editor.chain().focus().toggleHeading({ level: 3 }).run(), editor.isActive("heading", { level: 3 }))}
        <div className="w-px h-4 bg-border mx-1" />
        {btn("• List", () => editor.chain().focus().toggleBulletList().run(), editor.isActive("bulletList"))}
        {btn("1. List", () => editor.chain().focus().toggleOrderedList().run(), editor.isActive("orderedList"))}
        {btn("Quote", () => editor.chain().focus().toggleBlockquote().run(), editor.isActive("blockquote"))}
        {btn("</>", () => editor.chain().focus().toggleCodeBlock().run(), editor.isActive("codeBlock"))}
        <div className="w-px h-4 bg-border mx-1" />
        <button
          type="button"
          onClick={() => fileRef.current?.click()}
          className="text-muted hover:text-[#f1f1f5] text-sm px-2 py-1 rounded hover:bg-hover transition-colors"
        >
          Image
        </button>
        <input
          ref={fileRef}
          type="file"
          accept="image/*"
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) uploadImage(file);
            e.target.value = ""; // reset so same file can be re-uploaded
          }}
        />
      </div>

      {/* Editor area */}
      <EditorContent
        editor={editor}
        className="min-h-[400px] px-6 py-4 text-[#f1f1f5] focus:outline-none
          [&_.ProseMirror]:outline-none
          [&_.ProseMirror_h1]:text-3xl [&_.ProseMirror_h1]:font-bold [&_.ProseMirror_h1]:mb-4
          [&_.ProseMirror_h2]:text-2xl [&_.ProseMirror_h2]:font-bold [&_.ProseMirror_h2]:mb-3
          [&_.ProseMirror_h3]:text-xl [&_.ProseMirror_h3]:font-semibold [&_.ProseMirror_h3]:mb-2
          [&_.ProseMirror_p]:mb-3 [&_.ProseMirror_p]:leading-relaxed
          [&_.ProseMirror_blockquote]:border-l-4 [&_.ProseMirror_blockquote]:border-accent [&_.ProseMirror_blockquote]:pl-4 [&_.ProseMirror_blockquote]:text-muted
          [&_.ProseMirror_pre]:bg-hover [&_.ProseMirror_pre]:rounded-lg [&_.ProseMirror_pre]:p-4 [&_.ProseMirror_pre]:mb-3
          [&_.ProseMirror_ul]:list-disc [&_.ProseMirror_ul]:pl-6 [&_.ProseMirror_ul]:mb-3
          [&_.ProseMirror_ol]:list-decimal [&_.ProseMirror_ol]:pl-6 [&_.ProseMirror_ol]:mb-3
          [&_.ProseMirror_.is-editor-empty:first-child::before]:content-[attr(data-placeholder)] [&_.ProseMirror_.is-editor-empty:first-child::before]:text-muted [&_.ProseMirror_.is-editor-empty:first-child::before]:float-left [&_.ProseMirror_.is-editor-empty:first-child::before]:pointer-events-none"
      />
    </div>
  );
}
