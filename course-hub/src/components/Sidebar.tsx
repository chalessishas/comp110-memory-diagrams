"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, Plus, Settings, LogOut } from "lucide-react";
import { createClient } from "@/lib/supabase/client";
import { useRouter } from "next/navigation";
import type { Course } from "@/types";

export function Sidebar({ courses }: { courses: Course[] }) {
  const pathname = usePathname();
  const router = useRouter();
  const supabase = createClient();

  const activeCourses = courses.filter((c) => c.status === "active");

  async function handleSignOut() {
    await supabase.auth.signOut();
    router.push("/login");
  }

  return (
    <aside
      className="w-64 h-screen flex flex-col border-r p-4 shrink-0"
      style={{ backgroundColor: "var(--bg-surface)", borderColor: "var(--border)" }}
    >
      <Link href="/dashboard" className="text-lg font-semibold mb-6 block" style={{ color: "var(--text-primary)" }}>
        CourseHub
      </Link>

      <nav className="flex-1 space-y-1">
        <Link
          href="/dashboard"
          className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
            pathname === "/dashboard" ? "font-medium" : ""
          }`}
          style={{
            backgroundColor: pathname === "/dashboard" ? "var(--bg-primary)" : "transparent",
            color: "var(--text-primary)",
          }}
        >
          <LayoutDashboard size={16} />
          Dashboard
        </Link>

        <Link
          href="/new-course"
          className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors"
          style={{ color: "var(--accent)" }}
        >
          <Plus size={16} />
          New Course
        </Link>

        {activeCourses.length > 0 && (
          <div className="mt-4">
            <p className="px-3 text-xs font-medium uppercase tracking-wider mb-2" style={{ color: "var(--text-secondary)" }}>
              Courses
            </p>
            {activeCourses.map((course) => (
              <Link
                key={course.id}
                href={`/course/${course.id}`}
                className={`block px-3 py-2 rounded-lg text-sm truncate transition-colors ${
                  pathname.startsWith(`/course/${course.id}`) ? "font-medium" : ""
                }`}
                style={{
                  backgroundColor: pathname.startsWith(`/course/${course.id}`) ? "var(--bg-primary)" : "transparent",
                  color: "var(--text-primary)",
                }}
              >
                {course.title}
              </Link>
            ))}
          </div>
        )}
      </nav>

      <div className="space-y-1 border-t pt-4" style={{ borderColor: "var(--border)" }}>
        <Link
          href="/settings"
          className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm"
          style={{ color: "var(--text-secondary)" }}
        >
          <Settings size={16} />
          Settings
        </Link>
        <button
          onClick={handleSignOut}
          className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm w-full cursor-pointer"
          style={{ color: "var(--text-secondary)" }}
        >
          <LogOut size={16} />
          Sign Out
        </button>
      </div>
    </aside>
  );
}
