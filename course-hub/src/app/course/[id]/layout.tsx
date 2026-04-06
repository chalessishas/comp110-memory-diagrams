import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";

export default async function CourseLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) redirect("/login");

  const { data: course } = await supabase.from("courses").select("id").eq("id", id).single();
  if (!course) redirect("/dashboard");

  return <>{children}</>;
}
