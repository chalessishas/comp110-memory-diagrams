import Link from "next/link";
import { ArrowUpRight, BookOpen } from "lucide-react";
import type { Course } from "@/types";

export function CourseCard({ course }: { course: Course }) {
  return (
    <Link
      href={`/course/${course.id}`}
      className="ui-panel block p-6"
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-4 min-w-0">
          <div
            className="flex h-11 w-11 shrink-0 items-center justify-center"
            style={{ borderRadius: "10px", backgroundColor: "var(--bg-muted)", border: "1px solid var(--border)" }}
          >
            <BookOpen size={18} style={{ color: "var(--text-primary)" }} />
          </div>
          <div className="min-w-0">
            <div className="ui-kicker mb-3">Course</div>
            <h3 className="text-lg font-semibold truncate">{course.title}</h3>
            {course.professor && (
              <p className="text-sm mt-1 truncate" style={{ color: "var(--text-secondary)" }}>
                {course.professor}
              </p>
            )}
            {course.semester && (
              <p className="text-xs mt-2" style={{ color: "var(--text-muted)" }}>
                {course.semester}
              </p>
            )}
          </div>
        </div>
        <div
          className="flex h-9 w-9 shrink-0 items-center justify-center"
          style={{ borderRadius: "10px", backgroundColor: "var(--accent)", color: "white" }}
        >
          <ArrowUpRight size={15} />
        </div>
      </div>
    </Link>
  );
}
