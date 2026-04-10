import { createClient } from "@supabase/supabase-js";

// Service role client — NEVER use client-side. Only for admin operations
// that require bypassing RLS (e.g., deleting auth users).
export function createAdminClient() {
  const serviceKey = process.env.SUPABASE_SERVICE_ROLE_KEY;
  if (!serviceKey) {
    throw new Error("SUPABASE_SERVICE_ROLE_KEY not set — cannot perform admin operations");
  }
  return createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    serviceKey,
    { auth: { autoRefreshToken: false, persistSession: false } }
  );
}
