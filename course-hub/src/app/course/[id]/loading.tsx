import { Loader2 } from "lucide-react";

export default function Loading() {
  return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <Loader2 className="animate-spin" size={24} style={{ color: "var(--text-muted)" }} />
    </div>
  );
}
