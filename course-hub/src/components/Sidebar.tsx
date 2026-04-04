"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, Plus, LogOut, LogIn } from "lucide-react";
import { createClient } from "@/lib/supabase/client";
import { useRouter } from "next/navigation";
import type { Course } from "@/types";

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

  const activeCourses = courses.filter((c) => c.status === "active");

  async function handleSignOut() {
    await supabase.auth.signOut();
    router.push("/login");
  }

  return (
    <aside className="w-full shrink-0 p-4 pb-0 lg:w-[320px] lg:p-6">
      <div className="ui-panel p-4 md:p-5 lg:sticky lg:top-6">
        <div className="mb-6">
          <div className="ui-kicker mb-4">CourseHub</div>
          <Link href="/dashboard" className="block text-2xl font-semibold leading-tight" style={{ color: "var(--text-primary)" }}>
            Study in one quiet place.
          </Link>
          <p className="mt-2 text-sm" style={{ color: "var(--text-secondary)" }}>
            {isAuthenticated
              ? "Courses, practice, and progress in a monochrome workspace."
              : "Guest mode is open. Try the workflow first and sign in only when you want to save."}
          </p>
          {!isAuthenticated && (
            <div className="mt-4 rounded-[22px] px-4 py-4" style={{ border: "1px solid var(--border)", backgroundColor: "var(--bg-muted)" }}>
              <p className="text-[11px] font-semibold uppercase tracking-[0.24em]" style={{ color: "var(--text-secondary)" }}>
                Guest Mode
              </p>
              <p className="text-sm mt-2" style={{ color: "var(--text-secondary)" }}>
                Paste a syllabus, preview the outline, and decide later if you want an account.
              </p>
            </div>
          )}
          {isAuthenticated && userEmail && (
            <div className="mt-4">
              <span className="ui-badge">{userEmail}</span>
            </div>
          )}
        </div>

        <nav className="space-y-2">
          <Link
            href="/dashboard"
            className="flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-medium transition-colors"
            style={{
              backgroundColor: pathname === "/dashboard" ? "var(--accent)" : "rgba(247, 247, 244, 0.96)",
              color: pathname === "/dashboard" ? "white" : "var(--text-primary)",
              border: `1px solid ${pathname === "/dashboard" ? "var(--accent)" : "var(--border)"}`,
            }}
          >
            <LayoutDashboard size={16} />
            Dashboard
          </Link>

          <Link
            href="/new-course"
            className="flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-medium transition-colors"
            style={{
              backgroundColor: pathname === "/new-course" ? "var(--accent)" : "rgba(247, 247, 244, 0.96)",
              color: pathname === "/new-course" ? "white" : "var(--text-primary)",
              border: `1px solid ${pathname === "/new-course" ? "var(--accent)" : "var(--border)"}`,
            }}
          >
            <Plus size={16} />
            New Course
          </Link>
        </nav>

        {isAuthenticated && activeCourses.length > 0 && (
          <div className="mt-6 rounded-3xl p-4" style={{ border: "1px solid var(--border)", backgroundColor: "var(--bg-muted)" }}>
            <p className="text-[11px] font-semibold uppercase tracking-[0.24em] mb-3" style={{ color: "var(--text-secondary)" }}>
              Courses
            </p>
            <div className="space-y-2">
              {activeCourses.map((course) => {
                const isActive = pathname.startsWith(`/course/${course.id}`);
                return (
                  <Link
                    key={course.id}
                    href={`/course/${course.id}`}
                    className="block rounded-2xl px-4 py-3 text-sm transition-colors"
                    style={{
                      backgroundColor: isActive ? "white" : "transparent",
                      color: isActive ? "var(--text-primary)" : "var(--text-secondary)",
                      border: `1px solid ${isActive ? "var(--border-strong)" : "transparent"}`,
                      fontWeight: isActive ? 600 : 500,
                    }}
                  >
                    <span className="block truncate">{course.title}</span>
                  </Link>
                );
              })}
            </div>
          </div>
        )}

        <div className="mt-6 pt-5 flex flex-wrap gap-2" style={{ borderTop: "1px solid var(--border)" }}>
          {isAuthenticated ? (
            <button onClick={handleSignOut} className="ui-button-secondary !px-4 !py-3 !text-sm">
              <LogOut size={16} />
              Sign Out
            </button>
          ) : (
            <Link href="/login" className="ui-button-secondary !px-4 !py-3 !text-sm">
              <LogIn size={16} />
              Sign In
            </Link>
          )}
        </div>
      </div>
    </aside>
  );
}
