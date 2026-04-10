import { createClient } from "@/lib/supabase/server";
import { createAdminClient } from "@/lib/supabase/admin";
import { NextResponse } from "next/server";

// DELETE /api/account — permanently deletes the authenticated user and all their data.
// Cascade delete handles child tables (attempts, questions, element_mastery, etc.).
export async function DELETE() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  // Delete all courses (cascades to questions, attempts, lessons, mastery, etc.)
  const { data: courses } = await supabase.from("courses").select("id").eq("user_id", user.id);
  if (courses && courses.length > 0) {
    await supabase.from("courses").delete().in("id", courses.map((c) => c.id));
  }

  // Delete the auth account using admin client (requires SUPABASE_SERVICE_ROLE_KEY)
  try {
    const admin = createAdminClient();
    const { error } = await admin.auth.admin.deleteUser(user.id);
    if (error) {
      console.error("Failed to delete auth user:", error.message);
      return NextResponse.json({ error: "Failed to delete account" }, { status: 500 });
    }
  } catch (e) {
    console.error("Admin client error:", e);
    return NextResponse.json({ error: "Account deletion unavailable" }, { status: 503 });
  }

  return NextResponse.json({ ok: true });
}
