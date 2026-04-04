import { createClient } from "@/lib/supabase/server";
import { Sidebar } from "@/components/Sidebar";

export default async function DashboardLayout({ children }: { children: React.ReactNode }) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  const courses = user
    ? (await supabase
        .from("courses")
        .select("*")
        .eq("user_id", user.id)
        .order("created_at", { ascending: false })).data
    : [];

  return (
    <div className="min-h-screen lg:flex lg:gap-5">
      <Sidebar courses={courses ?? []} isAuthenticated={Boolean(user)} userEmail={user?.email ?? null} />
      <main className="flex-1 min-w-0 overflow-auto">
        <div className="ui-shell">{children}</div>
      </main>
    </div>
  );
}
