import Link from "next/link";
import { AlertCircle, ArrowRight, CheckCircle2, RotateCcw } from "lucide-react";

interface WrongAnswerNotebookItem {
  questionId: string;
  stem: string;
  knowledgePointTitle: string | null;
  lastWrongAnswer: string;
  correctAnswer: string;
  explanation: string | null;
  wrongCount: number;
  lastWrongAt: string;
  status: "needs_redo" | "fixed";
}

function formatShortDate(value: string) {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(value));
}

export function WrongAnswerNotebook({
  courseId,
  items,
}: {
  courseId: string;
  items: WrongAnswerNotebookItem[];
}) {
  return (
    <div id="wrong-notebook" className="ui-panel p-5 md:p-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <div className="ui-kicker mb-3">Wrong Notebook</div>
          <h3 className="text-2xl font-semibold tracking-wide">Keep the misses, not just the score.</h3>
          <p className="ui-copy mt-2 max-w-2xl">
            Every incorrect answer becomes a review target with the right answer and explanation attached.
          </p>
        </div>
        <Link href={`/course/${courseId}/practice`} className="ui-button-secondary">
          Redo Questions
          <RotateCcw size={14} />
        </Link>
      </div>

      {items.length === 0 ? (
        <div className="ui-empty mt-6">
          <p className="text-base font-medium mb-2">No wrong answers yet</p>
          <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
            Once you start doing practice, the questions you miss will collect here for review.
          </p>
        </div>
      ) : (
        <div className="space-y-3 mt-6">
          {items.slice(0, 8).map((item) => (
            <div key={item.questionId} className="ui-panel px-5 py-4">
              <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                <div>
                  <div className="flex flex-wrap gap-2">
                    <span
                      className="ui-badge"
                      style={{
                        backgroundColor: item.status === "needs_redo" ? "var(--danger-light, var(--bg-muted))" : "var(--success-light, var(--bg-muted))",
                      }}
                    >
                      {item.status === "needs_redo" ? (
                        <>
                          <AlertCircle size={12} style={{ color: "var(--danger)" }} />
                          Needs Redo
                        </>
                      ) : (
                        <>
                          <CheckCircle2 size={12} style={{ color: "var(--success)" }} />
                          Fixed Once
                        </>
                      )}
                    </span>
                    {item.knowledgePointTitle && <span className="ui-badge">{item.knowledgePointTitle}</span>}
                    <span className="ui-badge">{item.wrongCount} misses</span>
                  </div>
                  <p className="text-sm font-medium mt-3">{item.stem}</p>
                </div>
                <p className="text-xs shrink-0" style={{ color: "var(--text-muted)" }}>
                  Last miss: {formatShortDate(item.lastWrongAt)}
                </p>
              </div>

              <div className="grid gap-3 mt-4 lg:grid-cols-2">
                <div className="rounded-[20px] p-4" style={{ backgroundColor: "var(--bg-muted)" }}>
                  <p className="text-[11px] font-medium tracking-wide" style={{ color: "var(--text-muted)" }}>
                    Your Wrong Answer
                  </p>
                  <p className="text-sm mt-2 leading-relaxed">{item.lastWrongAnswer || "No answer recorded"}</p>
                </div>

                <div className="rounded-[20px] p-4" style={{ backgroundColor: "var(--bg-muted)" }}>
                  <p className="text-[11px] font-medium tracking-wide" style={{ color: "var(--text-muted)" }}>
                    Correct Answer
                  </p>
                  <p className="text-sm mt-2 leading-relaxed">{item.correctAnswer}</p>
                </div>
              </div>

              {item.explanation && (
                <div className="rounded-[20px] p-4 mt-3" style={{ backgroundColor: "var(--bg-muted)" }}>
                  <p className="text-[11px] font-medium tracking-wide" style={{ color: "var(--text-muted)" }}>
                    Why
                  </p>
                  <p className="text-sm mt-2 leading-relaxed" style={{ color: "var(--text-secondary)" }}>
                    {item.explanation}
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {items.length > 8 && (
        <div className="mt-5">
          <Link href={`/course/${courseId}/practice`} className="ui-button-ghost w-fit !px-0">
            See the rest in Practice
            <ArrowRight size={14} />
          </Link>
        </div>
      )}
    </div>
  );
}
