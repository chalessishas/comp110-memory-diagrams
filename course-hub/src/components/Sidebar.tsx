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
      className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium transition-colors whitespace-nowrap"
      style={{
        borderRadius: "8px",
        backgroundColor: isActive ? "var(--accent-light)" : "transparent",
        color: isActive ? "var(--accent)" : "var(--text-secondary)",
        fontWeight: isActive ? 600 : 500,
      }}
    >
      <Icon size={15} />
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
        backgroundColor: "var(--bg-surface)",
        borderBottom: "1px solid var(--border)",
      }}
    >
      <div className="max-w-7xl mx-auto px-5 md:px-8">
        {/* Main bar */}
        <div className="flex items-center justify-between h-14 gap-4">
          {/* Logo */}
          <Link href="/dashboard" className="flex items-center gap-2 shrink-0">
            <span className="text-base font-bold tracking-tight" style={{ color: "var(--text-primary)", letterSpacing: "-0.02em" }}>CourseHub</span>
          </Link>

          {/* Desktop nav — only core links, no course list */}
          <nav className="hidden md:flex items-center gap-0.5">
            <NavLink href="/dashboard" label={t("nav.dashboard")} icon={LayoutDashboard} pathname={pathname} />
            <NavLink href="/new-course" label={t("nav.newCourse")} icon={Plus} pathname={pathname} />
            <NavLink href="/dashboard/bank" label={t("nav.questionBank")} icon={Bookmark} pathname={pathname} />
          </nav>

          {/* Right side */}
          <div className="hidden md:flex items-center gap-1.5">
            <StreakBadge />
            <NavLink href="/settings" label={t("nav.settings")} icon={Settings} pathname={pathname} />
            {isAuthenticated ? (
              <button
                onClick={handleSignOut}
                className="flex items-center gap-2 px-3 py-1.5 text-sm cursor-pointer transition-colors"
                style={{ borderRadius: "8px", color: "var(--text-secondary)" }}
              >
                <LogOut size={15} />
                {t("nav.signOut")}
              </button>
            ) : (
              <Link
                href="/login"
                className="flex items-center gap-2 px-4 py-1.5 text-sm font-medium"
                style={{ borderRadius: "10px", backgroundColor: "var(--accent)", color: "white" }}
              >
                <LogIn size={15} />
                {t("nav.signIn")}
              </Link>
            )}
          </div>

          {/* Mobile hamburger */}
          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className="md:hidden p-2 cursor-pointer"
            style={{ borderRadius: "8px", color: "var(--text-primary)" }}
            aria-label={mobileOpen ? "Close menu" : "Open menu"}
          >
            {mobileOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>

        {/* Mobile dropdown */}
        {mobileOpen && (
          <div className="md:hidden pb-4 space-y-1" onClick={() => setMobileOpen(false)}>
            <NavLink href="/dashboard" label={t("nav.dashboard")} icon={LayoutDashboard} pathname={pathname} />
            <NavLink href="/new-course" label={t("nav.newCourse")} icon={Plus} pathname={pathname} />
            <NavLink href="/dashboard/bank" label={t("nav.questionBank")} icon={Bookmark} pathname={pathname} />
            <NavLink href="/settings" label={t("nav.settings")} icon={Settings} pathname={pathname} />
            <div className="pt-2" style={{ borderTop: "1px solid var(--border)" }}>
              {isAuthenticated ? (
                <button onClick={handleSignOut} className="flex items-center gap-2 px-3 py-1.5 text-sm cursor-pointer" style={{ color: "var(--text-secondary)" }}>
                  <LogOut size={15} /> {t("nav.signOut")}
                </button>
              ) : (
                <Link href="/login" className="flex items-center gap-2 px-3 py-1.5 text-sm" style={{ color: "var(--accent)" }}>
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
