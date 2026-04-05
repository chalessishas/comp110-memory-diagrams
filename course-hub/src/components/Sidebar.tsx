"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, Plus, LogOut, LogIn, Bookmark, Settings, Menu, X } from "lucide-react";
import { createClient } from "@/lib/supabase/client";
import { useRouter } from "next/navigation";
import { useState } from "react";
import type { Course } from "@/types";
import { UsagePanel } from "@/components/UsagePanel";

function NavLink({ href, label, icon: Icon, pathname }: { href: string; label: string; icon: typeof LayoutDashboard; pathname: string }) {
  const isActive = href === "/" ? pathname === href : pathname.startsWith(href);
  return (
    <Link
      href={href}
      className="flex items-center gap-2 px-3.5 py-2 rounded-xl text-sm font-medium transition-colors whitespace-nowrap"
      style={{
        backgroundColor: isActive ? "var(--accent)" : "transparent",
        color: isActive ? "white" : "var(--text-secondary)",
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

  const activeCourses = courses.filter((c) => c.status === "active");

  async function handleSignOut() {
    await supabase.auth.signOut();
    router.push("/login");
  }

  return (
    <header
      className="sticky top-0 z-40 ui-sidebar-wrapper"
      style={{
        backgroundColor: "rgba(252, 251, 249, 0.88)",
        backdropFilter: "blur(16px)",
        borderBottom: "1px solid var(--border)",
      }}
    >
      <div className="max-w-7xl mx-auto px-4 md:px-6">
        {/* Main bar */}
        <div className="flex items-center justify-between h-14 gap-4">
          {/* Logo */}
          <Link href="/dashboard" className="flex items-center gap-2 shrink-0">
            <span className="text-base font-bold" style={{ color: "var(--text-primary)" }}>CourseHub</span>
          </Link>

          {/* Desktop nav */}
          <nav className="hidden md:flex items-center gap-1">
            <NavLink href="/dashboard" label="Dashboard" icon={LayoutDashboard} pathname={pathname} />
            <NavLink href="/new-course" label="New Course" icon={Plus} pathname={pathname} />
            <NavLink href="/dashboard/bank" label="Question Bank" icon={Bookmark} pathname={pathname} />
            {activeCourses.map((course) => (
              <Link
                key={course.id}
                href={`/course/${course.id}`}
                className="px-3 py-1.5 rounded-xl text-sm transition-colors truncate max-w-[160px]"
                style={{
                  backgroundColor: pathname.startsWith(`/course/${course.id}`) ? "rgba(91, 108, 240, 0.1)" : "transparent",
                  color: pathname.startsWith(`/course/${course.id}`) ? "var(--accent)" : "var(--text-secondary)",
                  fontWeight: pathname.startsWith(`/course/${course.id}`) ? 600 : 400,
                }}
              >
                {course.title}
              </Link>
            ))}
          </nav>

          {/* Right side */}
          <div className="hidden md:flex items-center gap-2">
            <NavLink href="/settings" label="Settings" icon={Settings} pathname={pathname} />
            {isAuthenticated ? (
              <button
                onClick={handleSignOut}
                className="flex items-center gap-2 px-3 py-2 rounded-xl text-sm cursor-pointer transition-colors"
                style={{ color: "var(--text-secondary)" }}
              >
                <LogOut size={15} />
                Sign Out
              </button>
            ) : (
              <Link
                href="/login"
                className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium"
                style={{ backgroundColor: "var(--accent)", color: "white" }}
              >
                <LogIn size={15} />
                Sign In
              </Link>
            )}
          </div>

          {/* Mobile hamburger */}
          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className="md:hidden p-2 cursor-pointer rounded-xl"
            style={{ color: "var(--text-primary)" }}
          >
            {mobileOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>

        {/* Mobile dropdown */}
        {mobileOpen && (
          <div className="md:hidden pb-4 space-y-1" onClick={() => setMobileOpen(false)}>
            <NavLink href="/dashboard" label="Dashboard" icon={LayoutDashboard} pathname={pathname} />
            <NavLink href="/new-course" label="New Course" icon={Plus} pathname={pathname} />
            <NavLink href="/dashboard/bank" label="Question Bank" icon={Bookmark} pathname={pathname} />
            <NavLink href="/settings" label="Settings" icon={Settings} pathname={pathname} />
            {activeCourses.map((course) => (
              <Link
                key={course.id}
                href={`/course/${course.id}`}
                className="block px-3.5 py-2 rounded-xl text-sm truncate"
                style={{
                  color: pathname.startsWith(`/course/${course.id}`) ? "var(--accent)" : "var(--text-secondary)",
                  fontWeight: pathname.startsWith(`/course/${course.id}`) ? 600 : 400,
                }}
              >
                {course.title}
              </Link>
            ))}
            <div className="pt-2" style={{ borderTop: "1px solid var(--border)" }}>
              {isAuthenticated ? (
                <button onClick={handleSignOut} className="flex items-center gap-2 px-3.5 py-2 text-sm cursor-pointer" style={{ color: "var(--text-secondary)" }}>
                  <LogOut size={15} /> Sign Out
                </button>
              ) : (
                <Link href="/login" className="flex items-center gap-2 px-3.5 py-2 text-sm" style={{ color: "var(--accent)" }}>
                  <LogIn size={15} /> Sign In
                </Link>
              )}
            </div>
          </div>
        )}
      </div>
    </header>
  );
}
