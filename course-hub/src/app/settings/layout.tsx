import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";
import { Sidebar } from "@/components/Sidebar";

export default async function SettingsLayout({ children }: { children: React.ReactNode }) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();

  if (!user) redirect("/login");

  const { data: courses } = await supabase
    .from("courses")
    .select("*")
    .eq("user_id", user.id)
    .order("created_at", { ascending: false });

  return (
    <div className="min-h-screen lg:flex lg:gap-5">
      <Sidebar courses={courses ?? []} isAuthenticated={true} userEmail={user.email ?? null} />
      <main className="flex-1 min-w-0 overflow-auto">
        <div className="ui-shell">{children}</div>
      </main>
    </div>
  );
}
