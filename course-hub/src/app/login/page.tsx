"use client";

import { createClient } from "@/lib/supabase/client";
import { LogIn } from "lucide-react";

export default function LoginPage() {
  const supabase = createClient();

  async function signInWithGoogle() {
    await supabase.auth.signInWithOAuth({
      provider: "google",
      options: { redirectTo: `${window.location.origin}/auth/callback` },
    });
  }

  return (
    <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: "var(--bg-primary)" }}>
      <div className="p-8 rounded-2xl shadow-sm max-w-sm w-full" style={{ backgroundColor: "var(--bg-surface)" }}>
        <h1 className="text-2xl font-semibold mb-2" style={{ color: "var(--text-primary)" }}>CourseHub</h1>
        <p className="mb-6" style={{ color: "var(--text-secondary)" }}>
          Upload your syllabus. AI does the rest.
        </p>
        <button
          onClick={signInWithGoogle}
          className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-medium transition-colors cursor-pointer"
          style={{ backgroundColor: "var(--accent)", color: "white" }}
          onMouseOver={(e) => (e.currentTarget.style.backgroundColor = "var(--accent-hover)")}
          onMouseOut={(e) => (e.currentTarget.style.backgroundColor = "var(--accent)")}
        >
          <LogIn size={18} />
          Sign in with Google
        </button>
      </div>
    </div>
  );
}
