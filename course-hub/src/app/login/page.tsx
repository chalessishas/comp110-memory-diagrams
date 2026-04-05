"use client";

import { Suspense, useState } from "react";
import { createClient } from "@/lib/supabase/client";
import { LogIn, Mail, Loader2 } from "lucide-react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";

const AUTH_ERROR_MESSAGES: Record<string, string> = {
  auth_denied: "Sign-in was canceled or denied. Please try again.",
  auth_callback_missing_code: "That sign-in link is invalid or incomplete. Please try again.",
  auth_callback_failed: "We couldn't complete sign-in from that link. Please request a new one and try again.",
};

const DEFAULT_AUTH_ERROR = "We couldn't complete sign-in. Please try again.";

function LoginPageFallback() {
  return (
    <div className="min-h-screen px-6 py-10 flex items-center justify-center">
      <div
        className="max-w-md w-full rounded-[28px] p-8 md:p-10"
        style={{
          backgroundColor: "rgba(255, 255, 255, 0.92)",
          border: "1px solid var(--border)",
          boxShadow: "0 24px 80px rgba(0, 0, 0, 0.08)",
          backdropFilter: "blur(8px)",
        }}
      >
        <div
          className="inline-flex items-center rounded-full px-3 py-1 text-[11px] uppercase tracking-[0.28em] mb-6"
          style={{ border: "1px solid var(--border)", color: "var(--text-secondary)" }}
        >
          CourseHub
        </div>
        <h1 className="text-3xl font-semibold leading-tight mb-3" style={{ color: "var(--text-primary)" }}>
          Study without the setup.
        </h1>
        <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
          Upload your syllabus, build your course map, and keep your semester in one place.
        </p>
      </div>
    </div>
  );
}

function LoginPageContent() {
  const supabase = createClient();
  const searchParams = useSearchParams();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [dismissedAuthError, setDismissedAuthError] = useState(false);
  const authError = dismissedAuthError ? null : searchParams.get("error");
  const displayedError = error ?? (authError ? AUTH_ERROR_MESSAGES[authError] ?? DEFAULT_AUTH_ERROR : null);

  async function signInWithGoogle() {
    setDismissedAuthError(true);
    await supabase.auth.signInWithOAuth({
      provider: "google",
      options: { redirectTo: `${window.location.origin}/auth/callback` },
    });
  }

  async function handleEmailAuth(e: React.FormEvent) {
    e.preventDefault();
    setDismissedAuthError(true);
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
    <div className="min-h-screen px-6 py-10 flex items-center justify-center">
      <div
        className="max-w-md w-full rounded-[28px] p-8 md:p-10"
        style={{
          backgroundColor: "rgba(255, 255, 255, 0.92)",
          border: "1px solid var(--border)",
          boxShadow: "0 24px 80px rgba(0, 0, 0, 0.08)",
          backdropFilter: "blur(8px)",
        }}
      >
        <div
          className="inline-flex items-center rounded-full px-3 py-1 text-[11px] uppercase tracking-[0.28em] mb-6"
          style={{ border: "1px solid var(--border)", color: "var(--text-secondary)" }}
        >
          CourseHub
        </div>

        <div className="mb-6">
          <h1 className="text-3xl font-semibold leading-tight mb-3" style={{ color: "var(--text-primary)" }}>
            {mode === "login" ? "Welcome back." : "Create your workspace."}
          </h1>
          <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
            {mode === "login"
              ? "Sign in with email or Google to access your courses."
              : "Create an account with email and password to get started."}
          </p>
        </div>

        <div
          className="grid grid-cols-2 gap-1 rounded-2xl p-1 mb-6"
          style={{ backgroundColor: "var(--bg-muted)", border: "1px solid var(--border)" }}
        >
          <button
            type="button"
            onClick={() => {
              setDismissedAuthError(true);
              setMode("login");
              setError(null);
              setMessage(null);
            }}
            className="rounded-xl px-4 py-2.5 text-sm font-medium transition-colors cursor-pointer"
            style={{
              backgroundColor: mode === "login" ? "var(--accent)" : "transparent",
              color: mode === "login" ? "white" : "var(--text-secondary)",
            }}
          >
            Sign In
          </button>
          <button
            type="button"
            onClick={() => {
              setDismissedAuthError(true);
              setMode("signup");
              setError(null);
              setMessage(null);
            }}
            className="rounded-xl px-4 py-2.5 text-sm font-medium transition-colors cursor-pointer"
            style={{
              backgroundColor: mode === "signup" ? "var(--accent)" : "transparent",
              color: mode === "signup" ? "white" : "var(--text-secondary)",
            }}
          >
            Create Account
          </button>
        </div>

        <form onSubmit={handleEmailAuth} className="space-y-3 mb-4">
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => {
              setDismissedAuthError(true);
              setEmail(e.target.value);
            }}
            required
            className="w-full px-4 py-3 rounded-2xl text-sm outline-none"
            style={{ border: "1px solid var(--border)", backgroundColor: "var(--bg-muted)" }}
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => {
              setDismissedAuthError(true);
              setPassword(e.target.value);
            }}
            required
            minLength={6}
            className="w-full px-4 py-3 rounded-2xl text-sm outline-none"
            style={{ border: "1px solid var(--border)", backgroundColor: "var(--bg-muted)" }}
          />
          <button
            type="submit"
            disabled={loading}
            className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-2xl font-medium cursor-pointer disabled:opacity-50"
            style={{ backgroundColor: "var(--accent)", color: "white" }}
          >
            {loading ? <Loader2 size={16} className="animate-spin" /> : <Mail size={16} />}
            {mode === "login" ? "Sign In" : "Create Account"}
          </button>
        </form>

        <div className="flex items-center gap-3 mb-4">
          <div className="flex-1 h-px" style={{ backgroundColor: "var(--border)" }} />
          <span className="text-[11px] uppercase tracking-[0.28em]" style={{ color: "var(--text-secondary)" }}>or</span>
          <div className="flex-1 h-px" style={{ backgroundColor: "var(--border)" }} />
        </div>

        <button
          onClick={signInWithGoogle}
          className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-2xl text-sm cursor-pointer"
          style={{ border: "1px solid var(--border)", color: "var(--text-primary)", backgroundColor: "#ffffff" }}
        >
          <LogIn size={16} />
          Continue with Google
        </button>

        {displayedError && (
          <div
            className="mt-4 rounded-2xl px-4 py-3 text-xs"
            style={{ border: "1px solid var(--danger)", backgroundColor: "rgba(239, 68, 68, 0.06)", color: "var(--danger)" }}
          >
            {displayedError}
          </div>
        )}
        {message && (
          <div
            className="mt-4 rounded-2xl px-4 py-3 text-xs"
            style={{ border: "1px solid var(--success)", backgroundColor: "rgba(22, 163, 74, 0.06)", color: "var(--success)" }}
          >
            {message}
          </div>
        )}

        <div className="mt-6 space-y-3">
          <p className="text-xs" style={{ color: "var(--text-secondary)" }}>
            Sign in to save your courses and track progress across devices.
          </p>
          <Link href="/dashboard" className="ui-button-ghost w-full !justify-center">
            Continue as Guest
          </Link>
        </div>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={<LoginPageFallback />}>
      <LoginPageContent />
    </Suspense>
  );
}
