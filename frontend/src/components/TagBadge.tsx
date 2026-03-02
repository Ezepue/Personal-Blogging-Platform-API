const COLORS = [
  "bg-violet-900/50 text-violet-300",
  "bg-blue-900/50 text-blue-300",
  "bg-green-900/50 text-green-300",
  "bg-orange-900/50 text-orange-300",
  "bg-pink-900/50 text-pink-300",
];

function colorForTag(tag: string): string {
  let hash = 0;
  for (let i = 0; i < tag.length; i++) hash += tag.charCodeAt(i);
  return COLORS[hash % COLORS.length];
}

export default function TagBadge({ tag }: { tag: string }) {
  return (
    <span
      className={`text-xs px-2 py-0.5 rounded-full font-medium ${colorForTag(tag)}`}
    >
      {tag}
    </span>
  );
}
