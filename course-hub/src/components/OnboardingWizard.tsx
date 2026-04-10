"use client";

import { useState, useEffect } from "react";
import { ArrowRight, Check, Globe, GraduationCap, Calendar, Target, Sparkles } from "lucide-react";
import { saveOnboarding, type OnboardingPreferences } from "@/lib/onboarding";
import { useI18n, type Locale } from "@/lib/i18n";

const ROLES = [
  { key: "college", icon: "🎓" },
  { key: "highschool", icon: "📚" },
  { key: "selflearner", icon: "💡" },
  { key: "teacher", icon: "👩‍🏫" },
];

const GOALS = [
  { key: "organize", icon: "📋" },
  { key: "practice", icon: "📝" },
  { key: "review", icon: "🔄" },
  { key: "progress", icon: "📊" },
  { key: "lessons", icon: "📖" },
];

interface Props {
  onComplete: () => void;
}

export function OnboardingWizard({ onComplete }: Props) {
  const { t, setLocale } = useI18n();
  const [step, setStep] = useState(0);
  const [prefs, setPrefs] = useState<OnboardingPreferences>({
    language: "en",
    role: null,
    semester: null,
    goals: [],
    completed: false,
  });

  function handleNext() {
    if (step < steps.length - 1) {
      setStep(step + 1);
    } else {
      const final = { ...prefs, completed: true };
      saveOnboarding(final);
      setLocale(final.language as Locale);
      onComplete();
    }
  }

  function handleSkipAll() {
    const final = { ...prefs, completed: true };
    saveOnboarding(final);
    setLocale(final.language as Locale);
    onComplete();
  }

  function toggleGoal(key: string) {
    setPrefs((p) => ({
      ...p,
      goals: p.goals.includes(key) ? p.goals.filter((g) => g !== key) : [...p.goals, key],
    }));
  }

  const steps = [
    // Step 1: Role
    {
      icon: <GraduationCap size={28} style={{ color: "var(--accent)" }} />,
      titleKey: "onboarding.step1Title",
      subtitleKey: "onboarding.step1Subtitle",
      canSkip: true,
      content: (
        <div className="grid grid-cols-2 gap-3 mt-6">
          {ROLES.map((role) => (
            <button
              key={role.key}
              onClick={() => setPrefs((p) => ({ ...p, role: role.key as OnboardingPreferences["role"] }))}
              className="p-4 text-left cursor-pointer transition-all rounded-[20px]"
              style={{
                backgroundColor: prefs.role === role.key ? "var(--accent-light)" : "var(--bg-surface)",
                boxShadow: prefs.role === role.key
                  ? "inset 0 0 0 2px var(--accent)"
                  : "0 1px 4px rgba(0,0,0,0.03), 0 2px 8px rgba(0,0,0,0.02)",
              }}
            >
              <span className="text-2xl">{role.icon}</span>
              <p className="text-sm font-medium mt-2">{t(`onboarding.role.${role.key}`)}</p>
            </button>
          ))}
        </div>
      ),
    },
    // Step 2: Semester
    {
      icon: <Calendar size={28} style={{ color: "var(--accent)" }} />,
      titleKey: "onboarding.step2Title",
      subtitleKey: "onboarding.step2Subtitle",
      canSkip: true,
      content: (
        <div className="mt-6">
          <input
            value={prefs.semester ?? ""}
            onChange={(e) => setPrefs((p) => ({ ...p, semester: e.target.value || null }))}
            placeholder={t("onboarding.semesterPlaceholder")}
            className="ui-input w-full !py-3.5 !text-base"
          />
        </div>
      ),
    },
    // Step 3: Goals
    {
      icon: <Target size={28} style={{ color: "var(--accent)" }} />,
      titleKey: "onboarding.step3Title",
      subtitleKey: "onboarding.step3Subtitle",
      canSkip: true,
      content: (
        <div className="space-y-2 mt-6">
          {GOALS.map((goal) => (
            <button
              key={goal.key}
              onClick={() => toggleGoal(goal.key)}
              className="w-full flex items-center gap-3 p-4 text-left cursor-pointer transition-all rounded-[20px]"
              style={{
                backgroundColor: prefs.goals.includes(goal.key) ? "var(--accent-light)" : "var(--bg-surface)",
                boxShadow: prefs.goals.includes(goal.key)
                  ? "inset 0 0 0 2px var(--accent)"
                  : "0 1px 4px rgba(0,0,0,0.03), 0 2px 8px rgba(0,0,0,0.02)",
              }}
            >
              <span className="text-xl">{goal.icon}</span>
              <span className="text-sm font-medium">{t(`onboarding.goal.${goal.key}`)}</span>
              {prefs.goals.includes(goal.key) && (
                <Check size={16} className="ml-auto" style={{ color: "var(--accent)" }} />
              )}
            </button>
          ))}
        </div>
      ),
    },
    // Step 4: Ready
    {
      icon: <Sparkles size={28} style={{ color: "var(--accent)" }} />,
      titleKey: "onboarding.step4Title",
      subtitleKey: "onboarding.step4Subtitle",
      canSkip: false,
      content: (
        <div className="mt-6 space-y-3">
          <div className="p-4 rounded-[16px]" style={{ backgroundColor: "var(--bg-muted)" }}>
            <p className="text-xs font-medium mb-2" style={{ color: "var(--text-muted)" }}>{t("onboarding.language")}</p>
            <p className="text-sm font-medium">{prefs.language === "zh" ? "中文" : "English"}</p>
          </div>
          {prefs.role && (
            <div className="p-4 rounded-[16px]" style={{ backgroundColor: "var(--bg-muted)" }}>
              <p className="text-xs font-medium mb-2" style={{ color: "var(--text-muted)" }}>{t("onboarding.role")}</p>
              <p className="text-sm font-medium">{prefs.role ? t(`onboarding.role.${prefs.role}`) : ""}</p>
            </div>
          )}
          {prefs.semester && (
            <div className="p-4 rounded-[16px]" style={{ backgroundColor: "var(--bg-muted)" }}>
              <p className="text-xs font-medium mb-2" style={{ color: "var(--text-muted)" }}>{t("onboarding.semester")}</p>
              <p className="text-sm font-medium">{prefs.semester}</p>
            </div>
          )}
          {prefs.goals.length > 0 && (
            <div className="p-4 rounded-[16px]" style={{ backgroundColor: "var(--bg-muted)" }}>
              <p className="text-xs font-medium mb-2" style={{ color: "var(--text-muted)" }}>{t("onboarding.goals")}</p>
              <div className="flex flex-wrap gap-2">
                {prefs.goals.map((g) => (
                  <span key={g} className="ui-badge">{t(`onboarding.goal.${g}`)}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      ),
    },
  ];

  const currentStep = steps[step];
  const progress = ((step + 1) / steps.length) * 100;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-6" style={{ backgroundColor: "var(--bg-primary)" }}>
      <div className="w-full max-w-md">
        {/* Progress indicators */}
        <div className="flex items-center gap-2 mb-8">
          {steps.map((_, i) => (
            <div
              key={i}
              className="flex-1 h-[6px] rounded-full transition-all"
              style={{
                backgroundColor: i <= step ? "var(--accent)" : "var(--bg-muted)",
              }}
            />
          ))}
        </div>

        {/* Card */}
        <div className="ui-panel p-8">
          <div className="flex items-center gap-3 mb-2">
            {currentStep.icon}
          </div>
          <h1 className="text-2xl font-semibold mt-4 tracking-wide">
            {t(currentStep.titleKey)}
          </h1>
          <p className="text-sm mt-2" style={{ color: "var(--text-secondary)" }}>
            {t(currentStep.subtitleKey)}
          </p>

          {currentStep.content}

          {/* Actions */}
          <div className="flex items-center justify-between mt-8">
            <div>
              {step > 0 && (
                <button
                  onClick={() => setStep(step - 1)}
                  className="text-sm cursor-pointer"
                  style={{ color: "var(--text-secondary)" }}
                >
                  {t("onboarding.back")}
                </button>
              )}
            </div>
            <div className="flex items-center gap-3">
              {currentStep.canSkip && (
                <button
                  onClick={handleNext}
                  className="text-sm cursor-pointer"
                  style={{ color: "var(--text-secondary)" }}
                >
                  {t("onboarding.skip")}
                </button>
              )}
              <button
                onClick={handleNext}
                className="ui-button-primary"
              >
                {step === steps.length - 1 ? t("onboarding.getStarted") : t("onboarding.next")}
                <ArrowRight size={16} />
              </button>
            </div>
          </div>
        </div>

        {/* Skip all */}
        {step < steps.length - 1 && (
          <button
            onClick={handleSkipAll}
            className="w-full text-center text-xs mt-5 cursor-pointer"
            style={{ color: "var(--text-muted)" }}
          >
            {t("onboarding.skipSetup")}
          </button>
        )}
      </div>
    </div>
  );
}
