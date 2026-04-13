"use client";

import { useEffect, useState } from "react";
import type { Course } from "@/types";
import { courses } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Loader2, BookOpen } from "lucide-react";
import { ThemeToggle } from "@/components/theme/toggle";

export default function DashboardPage() {
  const [courseList, setCourseList] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    courses
      .list()
      .then(setCourseList)
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load courses"))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b">
        <div className="mx-auto flex h-14 max-w-4xl items-center justify-between px-4">
          <h1 className="text-lg font-semibold">CourseHub</h1>
          <ThemeToggle />
        </div>
      </header>

      <main className="mx-auto max-w-4xl px-4 py-6">
        <h2 className="mb-4 text-2xl font-semibold">Your Courses</h2>

        {loading && (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        )}

        {error && (
          <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4 text-center text-sm text-destructive">
            {error}
          </div>
        )}

        {!loading && !error && courseList.length === 0 && (
          <div className="py-20 text-center">
            <BookOpen className="mx-auto mb-3 h-12 w-12 text-muted-foreground" />
            <p className="text-muted-foreground">No courses yet. Create one to get started.</p>
          </div>
        )}

        <div className="grid gap-4 sm:grid-cols-2">
          {courseList.map((course) => (
            <a key={course.id} href={`/courses/${course.id}`}>
              <Card className="transition-colors hover:border-primary/50 cursor-pointer">
                <CardHeader>
                  <CardTitle className="text-base">{course.title}</CardTitle>
                  {course.description && (
                    <CardDescription className="line-clamp-2">{course.description}</CardDescription>
                  )}
                  <div className="flex items-center gap-2 pt-1 text-xs text-muted-foreground">
                    {course.professor && <span>{course.professor}</span>}
                    {course.semester && <span>· {course.semester}</span>}
                  </div>
                </CardHeader>
              </Card>
            </a>
          ))}
        </div>
      </main>
    </div>
  );
}
