import type { StudyMode } from "@/types";

export interface StudyModeBreakdown {
  solving: number;
  reviewing: number;
  studying: number;
  idle: number;
}

interface StudyDayRecord {
  totalMs: number;
  byMode: StudyModeBreakdown;
  courses: Record<string, { totalMs: number; byMode: StudyModeBreakdown }>;
}

interface StudyTrackerStore {
  days: Record<string, StudyDayRecord>;
}

export interface StudySummary {
  totalMs: number;
  byMode: StudyModeBreakdown;
}

const STORAGE_KEY = "coursehub.study-tracker";
export const STUDY_TRACKER_UPDATED_EVENT = "coursehub-study-tracker-updated";

function emptyBreakdown(): StudyModeBreakdown {
  return {
    solving: 0,
    reviewing: 0,
    studying: 0,
    idle: 0,
  };
}

function emptyDayRecord(): StudyDayRecord {
  return {
    totalMs: 0,
    byMode: emptyBreakdown(),
    courses: {},
  };
}

function getTodayKey(date = new Date()) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function canUseStorage() {
  return typeof window !== "undefined" && typeof window.localStorage !== "undefined";
}

function readStore(): StudyTrackerStore {
  if (!canUseStorage()) {
    return { days: {} };
  }

  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return { days: {} };
    const parsed = JSON.parse(raw) as StudyTrackerStore;
    return parsed?.days ? parsed : { days: {} };
  } catch {
    return { days: {} };
  }
}

function writeStore(store: StudyTrackerStore) {
  if (!canUseStorage()) return;
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(store));
  window.dispatchEvent(new Event(STUDY_TRACKER_UPDATED_EVENT));
}

export function recordStudyTime({
  courseId,
  mode,
  durationMs,
}: {
  courseId?: string | null;
  mode: StudyMode;
  durationMs: number;
}) {
  if (!canUseStorage() || durationMs <= 0) return;

  const cappedDuration = Math.min(durationMs, 60_000);
  const store = readStore();
  const todayKey = getTodayKey();
  const day = store.days[todayKey] ?? emptyDayRecord();

  day.totalMs += cappedDuration;
  day.byMode[mode] += cappedDuration;

  if (courseId) {
    const courseRecord = day.courses[courseId] ?? { totalMs: 0, byMode: emptyBreakdown() };
    courseRecord.totalMs += cappedDuration;
    courseRecord.byMode[mode] += cappedDuration;
    day.courses[courseId] = courseRecord;
  }

  store.days[todayKey] = day;
  writeStore(store);
}

export function getStudySummary(courseId?: string | null): StudySummary {
  const store = readStore();
  const day = store.days[getTodayKey()];
  if (!day) {
    return { totalMs: 0, byMode: emptyBreakdown() };
  }

  if (!courseId) {
    return { totalMs: day.totalMs, byMode: day.byMode };
  }

  const courseRecord = day.courses[courseId];
  if (!courseRecord) {
    return { totalMs: 0, byMode: emptyBreakdown() };
  }

  return { totalMs: courseRecord.totalMs, byMode: courseRecord.byMode };
}

export function formatDuration(ms: number) {
  const totalMinutes = Math.floor(ms / 60_000);
  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;

  if (hours === 0) return `${minutes}m`;
  if (minutes === 0) return `${hours}h`;
  return `${hours}h ${minutes}m`;
}
