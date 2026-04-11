import { Loader2 } from "lucide-react";

export default function NotesLoading() {
  return (
    <div className="flex items-center justify-center mt-20">
      <Loader2 size={22} className="animate-spin" style={{ color: "var(--text-muted)" }} />
    </div>
  );
}
