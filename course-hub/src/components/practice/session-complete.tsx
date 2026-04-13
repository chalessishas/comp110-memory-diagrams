"use client";

import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";

interface SessionCompleteProps {
  totalAnswered: number;
  totalCorrect: number;
  courseId: string;
  onRetry: () => void;
}

export function SessionComplete({ totalAnswered, totalCorrect, courseId, onRetry }: SessionCompleteProps) {
  const pct = totalAnswered > 0 ? Math.round((totalCorrect / totalAnswered) * 100) : 0;

  return (
    <div className="mx-auto max-w-md space-y-6 text-center">
      <h2 className="text-2xl font-semibold">Session Complete</h2>

      <div className="space-y-2">
        <p className="text-4xl font-bold">
          {totalCorrect}/{totalAnswered}{" "}
          <span className="text-lg font-normal text-muted-foreground">correct ({pct}%)</span>
        </p>
        <Progress value={pct} className="h-3" />
      </div>

      <div className="flex flex-col gap-3 pt-4">
        <Button onClick={onRetry} size="lg">
          Practice Again
        </Button>
        <Button variant="outline" size="lg" asChild>
          <a href={`/courses/${courseId}`}>Back to Course</a>
        </Button>
      </div>
    </div>
  );
}
