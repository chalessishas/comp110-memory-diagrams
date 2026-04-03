"use client";

import { useState } from "react";
import { createClient } from "@/lib/supabase/client";
import { LogIn, Mail, Loader2 } from "lucide-react";

export default function LoginPage() {
  const supabase = createClient();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  async function signInWithGoogle() {
    await supabase.auth.signInWithOAuth({
      provider: "google",
      options: { redirectTo: `${window.location.origin}/auth/callback` },
    });
  }

  async function handleEmailAuth(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setMessage(null);

    if (mode === "signup") {
      const { error } = await supabase.auth.signUp({
        email,
        password,
        options: { emailRedirectTo: `${window.location.origin}/auth/callback` },
      });
      if (error) {
        setError(error.message);
      } else {
        setMessage("Check your email to confirm your account.");
      }
    } else {
      const { error } = await supabase.auth.signInWithPassword({ email, password });
      if (error) {
        setError(error.message);
      } else {
        window.location.href = "/dashboard";
      }
    }
    setLoading(false);
  }

  return (
    <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: "var(--bg-primary)" }}>
      <div className="p-8 rounded-2xl shadow-sm max-w-sm w-full" style={{ backgroundColor: "var(--bg-surface)" }}>
        <h1 className="text-2xl font-semibold mb-2" style={{ color: "var(--text-primary)" }}>CourseHub</h1>
        <p className="mb-6" style={{ color: "var(--text-secondary)" }}>
          Upload your syllabus. AI does the rest.
        </p>

        <form onSubmit={handleEmailAuth} className="space-y-3 mb-4">
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full px-4 py-2.5 rounded-lg text-sm"
            style={{ border: "1px solid var(--border)", backgroundColor: "var(--bg-primary)" }}
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={6}
            className="w-full px-4 py-2.5 rounded-lg text-sm"
            style={{ border: "1px solid var(--border)", backgroundColor: "var(--bg-primary)" }}
          />
          <button
            type="submit"
            disabled={loading}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg font-medium cursor-pointer disabled:opacity-50"
            style={{ backgroundColor: "var(--accent)", color: "white" }}
          >
            {loading ? <Loader2 size={16} className="animate-spin" /> : <Mail size={16} />}
            {mode === "login" ? "Sign In" : "Create Account"}
          </button>
        </form>

        <button
          onClick={() => { setMode(mode === "login" ? "signup" : "login"); setError(null); setMessage(null); }}
          className="w-full text-center text-xs cursor-pointer mb-4"
          style={{ color: "var(--text-secondary)" }}
        >
          {mode === "login" ? "No account? Create one" : "Already have an account? Sign in"}
        </button>

        <div className="flex items-center gap-3 mb-4">
          <div className="flex-1 h-px" style={{ backgroundColor: "var(--border)" }} />
          <span className="text-xs" style={{ color: "var(--text-secondary)" }}>or</span>
          <div className="flex-1 h-px" style={{ backgroundColor: "var(--border)" }} />
        </div>

        <button
          onClick={signInWithGoogle}
          className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg text-sm cursor-pointer"
          style={{ border: "1px solid var(--border)", color: "var(--text-primary)" }}
        >
          <LogIn size={16} />
          Continue with Google
        </button>

        {error && <p className="text-xs mt-3" style={{ color: "var(--danger)" }}>{error}</p>}
        {message && <p className="text-xs mt-3" style={{ color: "var(--success)" }}>{message}</p>}
      </div>
    </div>
  );
}
