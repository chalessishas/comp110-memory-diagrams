import Link from "next/link";
import { ArrowUpRight, BookOpen } from "lucide-react";
import type { Course } from "@/types";

export function CourseCard({ course }: { course: Course }) {
  return (
    <Link
      href={`/course/${course.id}`}
      className="ui-panel block p-6 -[20px] hover:-translate-y-0.5"
    >
      {/* Title + arrow */}
      <div className="flex items-start justify-between gap-4 mb-4">
        <h3
          className="text-lg font-semibold leading-snug"
        >
          {course.title}
        </h3>
        <div
          className="flex h-8 w-8 shrink-0 items-center justify-center"
        >
          <ArrowUpRight size={14} strokeWidth={2} />
        </div>
      </div>

      {/* Meta info */}
      <div className="flex items-center gap-3 flex-wrap">
        {course.professor && (
          <span className="flex items-center gap-1.5 text-sm">
            <BookOpen size={13} strokeWidth={1.8} />
            {course.professor}
          </span>
        )}
        {course.semester && (
          <span
            className="text-xs px-2 py-0.5"
          >
            {course.semester}
          </span>
        )}
      </div>
    </Link>
  );
}
