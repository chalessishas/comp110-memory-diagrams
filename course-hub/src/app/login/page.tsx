"use client";

import { Suspense, useState } from "react";
import { createClient } from "@/lib/supabase/client";
import { LogIn, Mail, Loader2 } from "lucide-react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useI18n } from "@/lib/i18n";

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
        className="max-w-md w-full -[28px] p-8 md:p-10"
      >
        <div
          className="inline-flex items-center px-3 py-1 text-[11px] uppercase tracking-[0.28em] mb-6"
        >
          CourseHub
        </div>
        <h1 className="text-3xl font-semibold leading-tight mb-3">
          Study without the setup.
        </h1>
        <p className="text-sm">
          Upload your syllabus, build your course map, and keep your semester in one place.
        </p>
      </div>
    </div>
  );
}

function LoginPageContent() {
  const supabase = createClient();
  const searchParams = useSearchParams();
  const { t } = useI18n();
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
        className="max-w-md w-full -[28px] p-8 md:p-10"
      >
        <div
          className="inline-flex items-center px-3 py-1 text-[11px] uppercase tracking-[0.28em] mb-6"
        >
          CourseHub
        </div>

        <div className="mb-6">
          <h1 className="text-3xl font-semibold leading-tight mb-3">
            {mode === "login" ? t("login.welcome") : t("login.create")}
          </h1>
          <p className="text-sm">
            {mode === "login" ? t("login.signInDesc") : t("login.createDesc")}
          </p>
        </div>

        <div
          className="grid grid-cols-2 gap-1 p-1 mb-6"
        >
          <button
            type="button"
            onClick={() => {
              setDismissedAuthError(true);
              setMode("login");
              setError(null);
              setMessage(null);
            }}
            className="px-4 py-2.5 text-sm font-medium cursor-pointer"
          >
            {t("login.signIn")}
          </button>
          <button
            type="button"
            onClick={() => {
              setDismissedAuthError(true);
              setMode("signup");
              setError(null);
              setMessage(null);
            }}
            className="px-4 py-2.5 text-sm font-medium cursor-pointer"
          >
            {t("login.createAccount")}
          </button>
        </div>

        <form onSubmit={handleEmailAuth} className="space-y-3 mb-4">
          <input
            type="email"
            placeholder={t("settings.email")}
            value={email}
            onChange={(e) => {
              setDismissedAuthError(true);
              setEmail(e.target.value);
            }}
            required
            className="w-full px-4 py-3 text-sm outline-none"
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
            className="w-full px-4 py-3 text-sm outline-none"
          />
          <button
            type="submit"
            disabled={loading}
            className="w-full flex items-center justify-center gap-2 px-4 py-3 font-medium cursor-pointer disabled:opacity-50"
          >
            {loading ? <Loader2 size={16} className="animate-spin" /> : <Mail size={16} />}
            {mode === "login" ? t("login.signIn") : t("login.createAccount")}
          </button>
        </form>

        <div className="flex items-center gap-3 mb-4">
          <div className="flex-1 h-px" />
          <span className="text-[11px] uppercase tracking-[0.28em]">{t("misc.or")}</span>
          <div className="flex-1 h-px" />
        </div>

        <button
          onClick={signInWithGoogle}
          className="w-full flex items-center justify-center gap-2 px-4 py-3 text-sm cursor-pointer"
        >
          <LogIn size={16} />
          {t("login.continueGoogle")}
        </button>

        {displayedError && (
          <div
            className="mt-4 px-4 py-3 text-xs"
          >
            {displayedError}
          </div>
        )}
        {message && (
          <div
            className="mt-4 px-4 py-3 text-xs"
          >
            {message}
          </div>
        )}

        <div className="mt-6 space-y-3">
          <p className="text-xs">
            {t("login.bottomNote")}
          </p>
          <Link href="/dashboard" className="ui-button-ghost w-full !justify-center">
            {t("login.continueGuest")}
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
