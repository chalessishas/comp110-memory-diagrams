export interface OnboardingPreferences {
  language: "en" | "zh";
  role: "college" | "highschool" | "selflearner" | "teacher" | null;
  semester: string | null;
  goals: string[];
  completed: boolean;
}

const STORAGE_KEY = "coursehub.onboarding";

export function getOnboarding(): OnboardingPreferences {
  if (typeof window === "undefined") return defaultPrefs();
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : defaultPrefs();
  } catch {
    return defaultPrefs();
  }
}

export function saveOnboarding(prefs: OnboardingPreferences) {
  if (typeof window === "undefined") return;
  localStorage.setItem(STORAGE_KEY, JSON.stringify(prefs));
}

export function isOnboardingComplete(): boolean {
  return getOnboarding().completed;
}

function defaultPrefs(): OnboardingPreferences {
  return { language: "en", role: null, semester: null, goals: [], completed: false };
}
