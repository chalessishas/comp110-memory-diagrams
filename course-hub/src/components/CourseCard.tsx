import Link from "next/link";
import { BookOpen } from "lucide-react";
import type { Course } from "@/types";

export function CourseCard({ course }: { course: Course }) {
  return (
    <Link
      href={`/course/${course.id}`}
      className="block p-5 rounded-xl shadow-sm transition-shadow hover:shadow-md"
      style={{ backgroundColor: "var(--bg-surface)", border: "1px solid var(--border)" }}
    >
      <div className="flex items-start gap-3">
        <div className="p-2 rounded-lg" style={{ backgroundColor: "var(--bg-primary)" }}>
          <BookOpen size={20} style={{ color: "var(--accent)" }} />
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-medium truncate">{course.title}</h3>
          {course.professor && (
            <p className="text-sm mt-1 truncate" style={{ color: "var(--text-secondary)" }}>
              {course.professor}
            </p>
          )}
          {course.semester && (
            <p className="text-xs mt-1" style={{ color: "var(--text-secondary)" }}>
              {course.semester}
            </p>
          )}
        </div>
      </div>
    </Link>
  );
}
