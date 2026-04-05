const STORAGE_KEY = "coursehub.streaks";

export interface StreakData {
  currentStreak: number;
  longestStreak: number;
  lastActiveDate: string; // YYYY-MM-DD
  freezesUsed: number; // this month
  freezeAvailable: boolean;
  dailyGoal: number; // minutes
  todayMinutes: number;
  todayQuestions: number;
  history: Record<string, { minutes: number; questions: number; completed: boolean }>;
}

function todayKey(): string {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

function yesterdayKey(): string {
  const d = new Date();
  d.setDate(d.getDate() - 1);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

function defaultData(): StreakData {
  return {
    currentStreak: 0,
    longestStreak: 0,
    lastActiveDate: "",
    freezesUsed: 0,
    freezeAvailable: true,
    dailyGoal: 10,
    todayMinutes: 0,
    todayQuestions: 0,
    history: {},
  };
}

export function getStreakData(): StreakData {
  if (typeof window === "undefined") return defaultData();
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return defaultData();
    const data = JSON.parse(raw) as StreakData;

    const today = todayKey();
    const yesterday = yesterdayKey();

    if (data.lastActiveDate === today) {
      return data;
    }

    if (data.lastActiveDate === yesterday) {
      // Yesterday was active, streak continues — reset today's counters
      data.todayMinutes = 0;
      data.todayQuestions = 0;
      return data;
    }

    if (data.lastActiveDate && data.lastActiveDate !== today && data.lastActiveDate !== yesterday) {
      // Missed a day (or more)
      if (data.freezeAvailable && data.currentStreak > 0) {
        const missedDate = new Date(data.lastActiveDate);
        missedDate.setDate(missedDate.getDate() + 1);
        const missedKey = `${missedDate.getFullYear()}-${String(missedDate.getMonth() + 1).padStart(2, "0")}-${String(missedDate.getDate()).padStart(2, "0")}`;

        if (missedKey === yesterday) {
          // Only 1 day missed — use freeze
          data.freezeAvailable = false;
          data.freezesUsed++;
          data.history[missedKey] = { minutes: 0, questions: 0, completed: false };
        } else {
          data.currentStreak = 0;
        }
      } else {
        data.currentStreak = 0;
      }
    }

    data.todayMinutes = 0;
    data.todayQuestions = 0;

    return data;
  } catch {
    return defaultData();
  }
}

export function recordActivity(type: "question" | "minute") {
  if (typeof window === "undefined") return;
  const data = getStreakData();
  const today = todayKey();

  if (type === "question") data.todayQuestions++;
  if (type === "minute") data.todayMinutes++;

  const goalMet =
    data.todayMinutes >= data.dailyGoal ||
    data.todayQuestions >= Math.max(5, data.dailyGoal);

  if (!data.history[today]) {
    data.history[today] = { minutes: 0, questions: 0, completed: false };
  }
  data.history[today].minutes = data.todayMinutes;
  data.history[today].questions = data.todayQuestions;

  if (goalMet && !data.history[today].completed) {
    data.history[today].completed = true;

    if (data.lastActiveDate !== today) {
      data.currentStreak++;
      data.longestStreak = Math.max(data.longestStreak, data.currentStreak);
    }
  }

  data.lastActiveDate = today;

  localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  window.dispatchEvent(new Event("coursehub-streak-updated"));
}

export function setDailyGoal(minutes: number) {
  if (typeof window === "undefined") return;
  const data = getStreakData();
  data.dailyGoal = minutes;
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
}

export function getWeekHistory(): { day: string; completed: boolean; minutes: number }[] {
  const data = getStreakData();
  const result: { day: string; completed: boolean; minutes: number }[] = [];
  const today = new Date();

  for (let i = 6; i >= 0; i--) {
    const d = new Date(today);
    d.setDate(d.getDate() - i);
    const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
    const record = data.history[key];
    result.push({
      day: key,
      completed: record?.completed ?? false,
      minutes: record?.minutes ?? 0,
    });
  }

  return result;
}
