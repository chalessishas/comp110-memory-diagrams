"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, Plus, LogOut, LogIn, Bookmark, Settings, Menu, X } from "lucide-react";
import { createClient } from "@/lib/supabase/client";
import { useRouter } from "next/navigation";
import { useState } from "react";
import type { Course } from "@/types";
import { UsagePanel } from "@/components/UsagePanel";
import { useI18n } from "@/lib/i18n";
import { StreakBadge } from "@/components/StreakBadge";

function NavLink({ href, label, icon: Icon, pathname }: { href: string; label: string; icon: typeof LayoutDashboard; pathname: string }) {
  const isActive = pathname === href || (href !== "/dashboard" && pathname.startsWith(href + "/"));
  return (
    <Link
      href={href}
      className={`flex items-center gap-2 px-3.5 py-1.5 text-sm transition-all whitespace-nowrap rounded-xl ${
        isActive ? "font-semibold" : "font-medium"
      }`}
      style={{
        backgroundColor: isActive ? "var(--accent-light)" : "transparent",
        color: isActive ? "var(--accent)" : "var(--text-muted)",
      }}
    >
      <Icon size={15} strokeWidth={isActive ? 2.2 : 1.8} />
      {label}
    </Link>
  );
}

export function Sidebar({
  courses,
  isAuthenticated,
  userEmail,
}: {
  courses: Course[];
  isAuthenticated: boolean;
  userEmail?: string | null;
}) {
  const pathname = usePathname();
  const router = useRouter();
  const supabase = createClient();
  const [mobileOpen, setMobileOpen] = useState(false);
  const { locale, setLocale, t } = useI18n();

  const activeCourses = courses.filter((c) => c.status === "active");

  async function handleSignOut() {
    await supabase.auth.signOut();
    router.push("/login");
  }

  return (
    <header
      className="sticky top-0 z-40 ui-sidebar-wrapper"
      style={{
        backgroundColor: "color-mix(in srgb, var(--bg-surface) 85%, transparent)",
        backdropFilter: "blur(20px) saturate(1.2)",
        WebkitBackdropFilter: "blur(20px) saturate(1.2)",
      }}
    >
      <div className="max-w-7xl mx-auto px-5 md:px-8">
        {/* Main bar */}
        <div className="flex items-center justify-between h-14 gap-6">
          {/* Logo — left */}
          <Link href="/dashboard" className="flex items-center gap-2.5 shrink-0">
            <span
              className="text-base font-semibold"
              style={{ color: "var(--text-primary)", letterSpacing: "-0.01em" }}
            >
              CourseHub
            </span>
          </Link>

          {/* Desktop nav — center pills */}
          <nav className="hidden md:flex items-center gap-1 rounded-2xl px-1.5 py-1" style={{ backgroundColor: "var(--bg-muted)" }}>
            <NavLink href="/dashboard" label={t("nav.dashboard")} icon={LayoutDashboard} pathname={pathname} />
            <NavLink href="/new-course" label={t("nav.newCourse")} icon={Plus} pathname={pathname} />
            <NavLink href="/dashboard/bank" label={t("nav.questionBank")} icon={Bookmark} pathname={pathname} />
          </nav>

          {/* Right side */}
          <div className="hidden md:flex items-center gap-2">
            <StreakBadge />
            <NavLink href="/settings" label={t("nav.settings")} icon={Settings} pathname={pathname} />
            {isAuthenticated ? (
              <button
                onClick={handleSignOut}
                className="flex items-center gap-2 px-3.5 py-1.5 text-sm font-medium cursor-pointer transition-all rounded-xl"
                style={{ color: "var(--text-muted)" }}
              >
                <LogOut size={15} strokeWidth={1.8} />
                {t("nav.signOut")}
              </button>
            ) : (
              <Link
                href="/login"
                className="flex items-center gap-2 px-5 py-1.5 text-sm font-medium rounded-xl transition-all"
                style={{ backgroundColor: "var(--accent)", color: "white" }}
              >
                <LogIn size={15} />
                {t("nav.signIn")}
              </Link>
            )}
          </div>

          {/* Mobile hamburger */}
          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className="md:hidden p-2 cursor-pointer rounded-xl transition-colors"
            style={{ color: "var(--text-primary)" }}
          >
            {mobileOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>

        {/* Mobile dropdown */}
        {mobileOpen && (
          <div
            className="md:hidden pb-5 pt-2 space-y-1"
            onClick={() => setMobileOpen(false)}
          >
            <NavLink href="/dashboard" label={t("nav.dashboard")} icon={LayoutDashboard} pathname={pathname} />
            <NavLink href="/new-course" label={t("nav.newCourse")} icon={Plus} pathname={pathname} />
            <NavLink href="/dashboard/bank" label={t("nav.questionBank")} icon={Bookmark} pathname={pathname} />
            <NavLink href="/settings" label={t("nav.settings")} icon={Settings} pathname={pathname} />
            <div className="pt-3 mt-2">
              {isAuthenticated ? (
                <button
                  onClick={handleSignOut}
                  className="flex items-center gap-2 px-3.5 py-1.5 text-sm font-medium cursor-pointer rounded-xl"
                  style={{ color: "var(--text-muted)" }}
                >
                  <LogOut size={15} strokeWidth={1.8} /> {t("nav.signOut")}
                </button>
              ) : (
                <Link
                  href="/login"
                  className="flex items-center gap-2 px-3.5 py-1.5 text-sm font-medium rounded-xl"
                  style={{ color: "var(--accent)" }}
                >
                  <LogIn size={15} /> {t("nav.signIn")}
                </Link>
              )}
            </div>
          </div>
        )}
      </div>
    </header>
  );
}
