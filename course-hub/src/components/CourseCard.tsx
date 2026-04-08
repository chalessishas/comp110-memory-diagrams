import Link from "next/link";
import { ArrowUpRight, BookOpen } from "lucide-react";
import type { Course } from "@/types";

export function CourseCard({ course }: { course: Course }) {
  return (
    <Link
      href={`/course/${course.id}`}
      className="ui-panel block p-6 rounded-[20px] transition-all hover:-translate-y-0.5"
    >
      {/* Title + arrow */}
      <div className="flex items-start justify-between gap-4 mb-4">
        <h3
          className="text-lg font-semibold leading-snug"
          style={{ color: "var(--text-primary)" }}
        >
          {course.title}
        </h3>
        <div
          className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl transition-colors"
          style={{ backgroundColor: "var(--accent-light)", color: "var(--accent)" }}
        >
          <ArrowUpRight size={14} strokeWidth={2} />
        </div>
      </div>

      {/* Meta info */}
      <div className="flex items-center gap-3 flex-wrap">
        {course.professor && (
          <span className="flex items-center gap-1.5 text-sm" style={{ color: "var(--text-secondary)" }}>
            <BookOpen size={13} strokeWidth={1.8} />
            {course.professor}
          </span>
        )}
        {course.semester && (
          <span
            className="text-xs px-2 py-0.5 rounded-lg"
            style={{ backgroundColor: "var(--bg-muted)", color: "var(--text-muted)" }}
          >
            {course.semester}
          </span>
        )}
      </div>
    </Link>
  );
}
