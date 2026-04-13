"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import type { Course, Question } from "@/types";
import { courses as coursesApi, questions as questionsApi } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, Loader2, Play } from "lucide-react";

export default function CourseDetailPage() {
  const { id: courseId } = useParams<{ id: string }>();
  const [course, setCourse] = useState<Course | null>(null);
  const [questionCount, setQuestionCount] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!courseId) return;
    Promise.all([
      coursesApi.get(courseId),
      questionsApi.list(courseId),
    ])
      .then(([c, q]) => {
        setCourse(c);
        setQuestionCount(q.length);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [courseId]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (!course) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-muted-foreground">Course not found</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b">
        <div className="mx-auto flex h-14 max-w-4xl items-center gap-3 px-4">
          <a href="/dashboard" className="text-muted-foreground hover:text-foreground transition-colors">
            <ArrowLeft className="h-4 w-4" />
          </a>
          <h1 className="text-lg font-semibold truncate">{course.title}</h1>
          <Badge variant="secondary" className="ml-auto shrink-0">
            {course.status}
          </Badge>
        </div>
      </header>

      <main className="mx-auto max-w-4xl px-4 py-6 space-y-6">
        {/* Course info */}
        <div className="space-y-1">
          {course.description && <p className="text-muted-foreground">{course.description}</p>}
          <div className="flex gap-3 text-sm text-muted-foreground">
            {course.professor && <span>{course.professor}</span>}
            {course.semester && <span>· {course.semester}</span>}
          </div>
        </div>

        {/* Quick actions */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <a href={`/courses/${courseId}/practice`}>
            <Card className="transition-colors hover:border-primary/50 cursor-pointer">
              <CardHeader className="pb-2">
                <CardTitle className="flex items-center gap-2 text-base">
                  <Play className="h-4 w-4 text-primary" />
                  Practice
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  {questionCount !== null ? `${questionCount} questions available` : "Loading..."}
                </p>
              </CardContent>
            </Card>
          </a>
        </div>
      </main>
    </div>
  );
}
