import { Loader2 } from "lucide-react";

export default function DashboardLoading() {
  return (
    <div className="flex items-center justify-center mt-24">
      <Loader2 size={22} className="animate-spin" style={{ color: "var(--text-muted)" }} />
    </div>
  );
}
