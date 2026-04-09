"use client";

import { useEffect, useRef, useState } from "react";
import {
  BrainCircuit,
  CheckCircle2,
  Languages,
  MessageCircleQuestion,
  Mic,
  NotebookPen,
  Save,
  Sparkles,
  Square,
  Tag,
} from "lucide-react";
import type { CourseNote, NoteSource, OrganizedStudyNote } from "@/types";
import { toCourseNote, toCourseNoteCreatePayload, type CourseNoteRow } from "@/lib/course-notes";

type DictationTarget = { type: "transcript" } | { type: "clarification"; index: number };

interface SpeechRecognitionAlternativeLike {
  transcript: string;
}

interface SpeechRecognitionResultLike {
  isFinal: boolean;
  0: SpeechRecognitionAlternativeLike;
}

interface SpeechRecognitionEventLike extends Event {
  resultIndex: number;
  results: ArrayLike<SpeechRecognitionResultLike>;
  error?: string;
}

interface SpeechRecognitionLike {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  onstart: (() => void) | null;
  onend: (() => void) | null;
  onerror: ((event: SpeechRecognitionEventLike) => void) | null;
  onresult: ((event: SpeechRecognitionEventLike) => void) | null;
  start: () => void;
  stop: () => void;
}

interface SpeechRecognitionConstructor {
  new (): SpeechRecognitionLike;
}

declare global {
  interface Window {
    SpeechRecognition?: SpeechRecognitionConstructor;
    webkitSpeechRecognition?: SpeechRecognitionConstructor;
  }
}

function joinSpeech(base: string, chunk: string) {
  const left = base.trim();
  const right = chunk.trim();
  if (!left) return right;
  if (!right) return left;
  return `${left} ${right}`;
}

function formatNoteDate(value: string) {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(value));
}

export function VoiceNotesPanel({
  courseId,
  knowledgePoints,
  initialNotes,
}: {
  courseId: string;
  knowledgePoints: { id: string; title: string }[];
  initialNotes: CourseNote[];
}) {
  const [notes, setNotes] = useState<CourseNote[]>(initialNotes);
  const [transcript, setTranscript] = useState("");
  const [draft, setDraft] = useState<OrganizedStudyNote | null>(null);
  const [clarificationAnswers, setClarificationAnswers] = useState<string[]>([]);
  const [selectedKnowledgePointId, setSelectedKnowledgePointId] = useState("");
  const [language, setLanguage] = useState("en-US");
  const [recordingTarget, setRecordingTarget] = useState<DictationTarget>({ type: "transcript" });
  const [interimText, setInterimText] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [organizing, setOrganizing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [lastInputSource, setLastInputSource] = useState<NoteSource>("voice");
  const recognitionRef = useRef<SpeechRecognitionLike | null>(null);

  useEffect(() => {
    setNotes(initialNotes);
  }, [initialNotes]);

  useEffect(() => {
    if (typeof navigator !== "undefined" && navigator.language) {
      setLanguage(navigator.language);
    }
  }, []);

  useEffect(() => {
    return () => {
      recognitionRef.current?.stop();
    };
  }, []);

  function getRecognitionConstructor() {
    if (typeof window === "undefined") return null;
    return window.SpeechRecognition ?? window.webkitSpeechRecognition ?? null;
  }

  function appendToTarget(target: DictationTarget, text: string) {
    if (!text.trim()) return;

    if (target.type === "transcript") {
      setTranscript((prev) => joinSpeech(prev, text));
      setDraft(null);
      setClarificationAnswers([]);
      return;
    }

    setClarificationAnswers((prev) =>
      prev.map((answer, index) => (index === target.index ? joinSpeech(answer, text) : answer))
    );
  }

  function startDictation(target: DictationTarget) {
    const Recognition = getRecognitionConstructor();
    if (!Recognition) {
      setError("This browser does not expose speech recognition. You can still type into the note box.");
      return;
    }

    setError(null);
    setStatus(null);
    setInterimText("");
    setRecordingTarget(target);
    setLastInputSource("voice");

    recognitionRef.current?.stop();

    const recognition = new Recognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = language;

    recognition.onstart = () => {
      setIsRecording(true);
    };

    recognition.onresult = (event) => {
      const finalChunks: string[] = [];
      let liveChunk = "";

      for (let index = event.resultIndex; index < event.results.length; index += 1) {
        const result = event.results[index];
        const chunk = result[0]?.transcript?.trim();
        if (!chunk) continue;
        if (result.isFinal) {
          finalChunks.push(chunk);
        } else {
          liveChunk = chunk;
        }
      }

      for (const chunk of finalChunks) {
        appendToTarget(target, chunk);
      }

      setInterimText(liveChunk);
    };

    recognition.onerror = (event) => {
      setError(event.error ? `Speech recognition error: ${event.error}` : "Speech recognition failed.");
    };

    recognition.onend = () => {
      setIsRecording(false);
      setInterimText("");
      recognitionRef.current = null;
    };

    recognitionRef.current = recognition;
    recognition.start();
  }

  function stopDictation() {
    recognitionRef.current?.stop();
  }

  async function organizeNote() {
    if (!transcript.trim()) {
      setError("Say something first, or paste a note into the transcript box.");
      return;
    }

    setOrganizing(true);
    setError(null);
    setStatus(null);

    const res = await fetch(`/api/courses/${courseId}/notes/organize`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        transcript,
        knowledge_point_id: selectedKnowledgePointId || null,
        clarification_answers: clarificationAnswers.filter((answer) => answer.trim().length > 0),
        source: lastInputSource,
      }),
    });

    const data = await res.json();
    if (!res.ok) {
      setError(data.error?.formErrors?.join(", ") || data.error || "Failed to organize note");
      setOrganizing(false);
      return;
    }

    const note = data.note as OrganizedStudyNote;
    setDraft(note);
    setClarificationAnswers((prev) =>
      note.clarification_questions.map((_, index) => prev[index] ?? "")
    );
    if (!selectedKnowledgePointId && note.matched_knowledge_point_id) {
      setSelectedKnowledgePointId(note.matched_knowledge_point_id);
    }
    setStatus(
      note.clarification_questions.length > 0
        ? "AI organized the note and highlighted the gaps it wants to check with you."
        : "AI organized the note. It looks clear enough to save."
    );
    setOrganizing(false);
  }

  async function handleSave() {
    if (!draft) {
      setError("Organize the note with AI before saving it.");
      return;
    }

    setSaving(true);
    setError(null);

    const selectedKnowledgePoint = knowledgePoints.find((item) => item.id === selectedKnowledgePointId) ?? null;
    const knowledgePointId = selectedKnowledgePoint?.id ?? draft.matched_knowledge_point_id ?? null;

    const res = await fetch(`/api/courses/${courseId}/notes`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(
        toCourseNoteCreatePayload({
          knowledgePointId,
          transcript,
          source: lastInputSource,
          organized: draft,
          clarificationAnswers,
        })
      ),
    });

    const data = await res.json();
    if (!res.ok) {
      setError(data.error?.formErrors?.join(", ") || data.error || "Failed to save note");
      setSaving(false);
      return;
    }

    const inserted = toCourseNote(
      data.note as CourseNoteRow,
      selectedKnowledgePoint?.title ?? draft.matched_knowledge_point_title ?? null
    );
    setNotes((prev) => [inserted, ...prev]);

    setTranscript("");
    setDraft(null);
    setClarificationAnswers([]);
    setSelectedKnowledgePointId("");
    setStatus("Note saved to this course.");
    setSaving(false);
  }

  const speechSupported = Boolean(getRecognitionConstructor());
  const canRefine = clarificationAnswers.some((answer) => answer.trim().length > 0);

  return (
    <div className="ui-panel p-5 md:p-6">
      {/* Header */}
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <div className="ui-kicker mb-3">Voice Notes</div>
          <h3 className="text-2xl font-semibold tracking-wide">Talk it out. We will turn it into study notes.</h3>
          <p className="ui-copy mt-2 max-w-2xl">
            Speak your understanding out loud, let AI clean it up, then answer a couple of follow-up questions if the idea is still fuzzy.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <span className="ui-badge">
            <NotebookPen size={12} />
            {notes.length} notes
          </span>
          <span className="ui-badge">
            <Languages size={12} />
            {language}
          </span>
        </div>
      </div>

      {/* Recording area */}
      <div className="-[20px] p-5 mt-6">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="text-sm font-medium">1. Speak or paste the raw note</p>
            <p className="text-xs mt-1">
              Use the mic for the main note, then use the smaller mic buttons below if AI asks you to clarify something.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            {isRecording ? (
              <button onClick={stopDictation} className="ui-button-primary">
                <Square size={14} />
                Stop Recording
              </button>
            ) : (
              <button onClick={() => startDictation({ type: "transcript" })} className="ui-button-primary" disabled={!speechSupported}>
                <Mic size={14} />
                Talk Note
              </button>
            )}
            <button onClick={organizeNote} disabled={organizing || !transcript.trim()} className="ui-button-secondary disabled:opacity-40">
              <Sparkles size={14} />
              {organizing ? "Organizing..." : "Organize with AI"}
            </button>
          </div>
        </div>

        {!speechSupported && (
          <p className="text-xs mt-3">
            Browser speech recognition is not available here, so this panel falls back to typed notes.
          </p>
        )}

        <div className="grid gap-3 mt-4 lg:grid-cols-[220px_minmax(0,1fr)]">
          <div>
            <label className="text-[11px] font-medium tracking-wide">
              Knowledge Point
            </label>
            <select
              value={selectedKnowledgePointId}
              onChange={(event) => setSelectedKnowledgePointId(event.target.value)}
              className="ui-input mt-2"
            >
              <option value="">Let AI match it</option>
              {knowledgePoints.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.title}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-[11px] font-medium tracking-wide">
              Transcript
            </label>
            <textarea
              value={transcript}
              onChange={(event) => {
                setTranscript(event.target.value);
                setLastInputSource("text");
                setDraft(null);
                setClarificationAnswers([]);
              }}
              rows={6}
              className="ui-textarea mt-2"
              placeholder="Explain the concept in your own words, say what is confusing, or dictate what the teacher emphasized."
            />
            {isRecording && recordingTarget.type === "transcript" && interimText && (
              <p className="text-xs mt-2">
                Listening: {interimText}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="-[20px] px-5 py-3 mt-4">
          <p className="text-sm">{error}</p>
        </div>
      )}

      {/* Status */}
      {status && (
        <div className="-[20px] px-5 py-3 mt-4">
          <p className="text-sm">{status}</p>
        </div>
      )}

      {/* Draft */}
      {draft && (
        <div className="space-y-4 mt-6">
          <div className="ui-panel p-6">
            <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
              <div>
                <div className="ui-kicker mb-3">AI Note Draft</div>
                <h4 className="text-xl font-semibold tracking-wide">{draft.title}</h4>
                <p className="ui-copy mt-2 max-w-3xl">{draft.summary}</p>
              </div>
              {draft.matched_knowledge_point_title && (
                <span className="ui-badge">
                  <Tag size={12} />
                  {draft.matched_knowledge_point_title}
                </span>
              )}
            </div>

            <div className="grid gap-4 mt-5 lg:grid-cols-2">
              <div className="-[20px] p-5">
                <p className="text-[11px] font-medium tracking-wide">
                  Key Points
                </p>
                <div className="space-y-2 mt-3">
                  {draft.key_points.map((item) => (
                    <p key={item} className="text-sm leading-relaxed">{item}</p>
                  ))}
                </div>
              </div>

              <div className="-[20px] p-5">
                <p className="text-[11px] font-medium tracking-wide">
                  What Still Feels Fuzzy
                </p>
                <div className="space-y-2 mt-3">
                  {draft.confusing_points.length > 0 ? (
                    draft.confusing_points.map((item) => (
                      <p key={item} className="text-sm leading-relaxed">{item}</p>
                    ))
                  ) : (
                    <p className="text-sm">
                      AI thinks your explanation is already fairly clear.
                    </p>
                  )}
                </div>
              </div>
            </div>

            {draft.next_action && (
              <div className="-[20px] p-5 mt-4">
                <div className="flex items-center gap-2 text-[11px] font-medium tracking-wide">
                  <BrainCircuit size={14} />
                  Next Action
                </div>
                <p className="text-sm mt-2 leading-relaxed">{draft.next_action}</p>
              </div>
            )}
          </div>

          {/* Clarification questions */}
          {draft.clarification_questions.length > 0 && (
            <div className="-[20px] p-5">
              <div className="flex items-center gap-2">
                <MessageCircleQuestion size={16} />
                <p className="text-sm font-medium">2. Answer the follow-up questions</p>
              </div>
              <p className="text-xs mt-2">
                If you do not want to type, click the mic beside a question and answer it out loud.
              </p>

              <div className="space-y-4 mt-4">
                {draft.clarification_questions.map((question, index) => (
                  <div key={question}>
                    <p className="text-sm font-medium">{question}</p>
                    <div className="flex gap-2 mt-2">
                      <input
                        value={clarificationAnswers[index] ?? ""}
                        onChange={(event) =>
                          setClarificationAnswers((prev) =>
                            prev.map((answer, answerIndex) =>
                              answerIndex === index ? event.target.value : answer
                            )
                          )
                        }
                        className="ui-input"
                        placeholder="Reply here or use the mic"
                      />
                      <button
                        type="button"
                        onClick={() => startDictation({ type: "clarification", index })}
                        className="ui-icon-button shrink-0"
                        disabled={!speechSupported}
                      >
                        <Mic size={14} />
                      </button>
                    </div>
                    {isRecording && recordingTarget.type === "clarification" && recordingTarget.index === index && interimText && (
                      <p className="text-xs mt-2">
                        Listening: {interimText}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Save / Refine buttons */}
          <div className="flex flex-wrap gap-2">
            <button onClick={handleSave} disabled={saving} className="ui-button-primary">
              <Save size={14} />
              {saving ? "Saving..." : "Save Note"}
            </button>
            {draft.clarification_questions.length > 0 && (
              <button onClick={organizeNote} disabled={organizing || !canRefine} className="ui-button-secondary disabled:opacity-40">
                <Sparkles size={14} />
                {organizing ? "Refining..." : "Refine with Answers"}
              </button>
            )}
          </div>
        </div>
      )}

      {/* Saved notes list */}
      <div className="mt-8">
        <div className="ui-kicker mb-4">Saved Notes</div>
        {notes.length === 0 ? (
          <div className="ui-empty">
            <p className="text-base font-medium mb-2">No notes yet</p>
            <p className="text-sm">
              Save a voice note and it will stay attached to this course.
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {notes.map((note) => (
              <div key={note.id} className="ui-panel px-5 py-4">
                <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                  <div>
                    <div className="flex flex-wrap gap-2">
                      <span className="ui-badge">
                        <CheckCircle2 size={12} />
                        {note.source === "voice" ? "Voice Note" : "Typed Note"}
                      </span>
                      {note.knowledge_point_title && <span className="ui-badge">{note.knowledge_point_title}</span>}
                    </div>
                    <h4 className="text-base font-medium mt-3">{note.title}</h4>
                    <p className="text-sm mt-2 leading-relaxed">
                      {note.summary}
                    </p>
                  </div>
                  <p className="text-xs shrink-0">
                    {formatNoteDate(note.created_at)}
                  </p>
                </div>

                <div className="space-y-2 mt-4">
                  {note.key_points.map((item) => (
                    <p key={item} className="text-sm leading-relaxed">{item}</p>
                  ))}
                </div>

                {note.next_action && (
                  <p className="text-sm mt-4 leading-relaxed">
                    <span className="font-medium">Next:</span> {note.next_action}
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
