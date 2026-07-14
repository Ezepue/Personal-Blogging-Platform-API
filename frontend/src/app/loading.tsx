export default function Loading() {
  return (
    <div className="flex items-center justify-center min-h-[50vh]" aria-label="Loading" role="status">
      <div className="w-8 h-8 border-2 border-accent border-t-transparent rounded-full animate-spin" />
    </div>
  );
}
