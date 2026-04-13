import { createClient } from "@/lib/supabase/server";
import { NextResponse } from "next/server";

export async function GET(request: Request) {
  const { searchParams, origin } = new URL(request.url);
  const code = searchParams.get("code");
  const loginUrl = new URL("/auth/login", origin);

  if (searchParams.get("error") || searchParams.get("error_description")) {
    loginUrl.searchParams.set("error", "auth_denied");
    return NextResponse.redirect(loginUrl);
  }

  if (!code) {
    loginUrl.searchParams.set("error", "auth_callback_missing_code");
    return NextResponse.redirect(loginUrl);
  }

  const supabase = await createClient();
  const { error } = await supabase.auth.exchangeCodeForSession(code);

  if (error) {
    loginUrl.searchParams.set("error", "auth_callback_failed");
    return NextResponse.redirect(loginUrl);
  }

  const next = searchParams.get("next") ?? "/dashboard";
  return NextResponse.redirect(new URL(next, origin));
}
