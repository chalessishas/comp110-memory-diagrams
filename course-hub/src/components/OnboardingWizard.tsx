"use client";

import { useState, useEffect } from "react";
import { ArrowRight, Check, Globe, GraduationCap, Calendar, Target, Sparkles } from "lucide-react";
import { saveOnboarding, type OnboardingPreferences } from "@/lib/onboarding";
import { useI18n, type Locale } from "@/lib/i18n";

const ROLES = [
  { key: "college", en: "College Student", zh: "大学生", icon: "🎓" },
  { key: "highschool", en: "High School", zh: "高中生", icon: "📚" },
  { key: "selflearner", en: "Self-Learner", zh: "自学者", icon: "💡" },
  { key: "teacher", en: "Teacher / TA", zh: "教师 / 助教", icon: "👩‍🏫" },
];

const GOALS = [
  { key: "organize", en: "Organize my courses", zh: "整理课程大纲", icon: "📋" },
  { key: "practice", en: "Practice with AI questions", zh: "AI 出题练习", icon: "📝" },
  { key: "review", en: "Spaced repetition review", zh: "间隔重复复习", icon: "🔄" },
  { key: "progress", en: "Track my mastery", zh: "追踪学习进度", icon: "📊" },
  { key: "lessons", en: "AI-generated lessons", zh: "AI 生成课程内容", icon: "📖" },
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

  const isZh = prefs.language === "zh";

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
      title: "What describes you best?",
      titleZh: "你是哪类学习者？",
      subtitle: "This helps us customize your experience.",
      subtitleZh: "帮助我们为你定制体验。",
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
              <p className="text-sm font-medium mt-2">{isZh ? role.zh : role.en}</p>
            </button>
          ))}
        </div>
      ),
    },
    // Step 2: Semester
    {
      icon: <Calendar size={28} style={{ color: "var(--accent)" }} />,
      title: "What semester are you in?",
      titleZh: "你现在是哪个学期？",
      subtitle: "We'll organize your dashboard around this.",
      subtitleZh: "我们会按学期组织你的仪表盘。",
      canSkip: true,
      content: (
        <div className="mt-6">
          <input
            value={prefs.semester ?? ""}
            onChange={(e) => setPrefs((p) => ({ ...p, semester: e.target.value || null }))}
            placeholder={isZh ? "例如：2026 春季" : "e.g. Spring 2026"}
            className="ui-input w-full !py-3.5 !text-base"
          />
        </div>
      ),
    },
    // Step 3: Goals
    {
      icon: <Target size={28} style={{ color: "var(--accent)" }} />,
      title: "What matters most to you?",
      titleZh: "你最看重什么功能？",
      subtitle: "Pick 1-3. We'll highlight these features for you.",
      subtitleZh: "选 1-3 个，我们会为你重点推荐。",
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
              <span className="text-sm font-medium">{isZh ? goal.zh : goal.en}</span>
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
      title: "You're all set!",
      titleZh: "设置完成！",
      subtitle: "Here's what we've configured for you.",
      subtitleZh: "以下是你的个性化配置。",
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
              <p className="text-sm font-medium">{ROLES.find((r) => r.key === prefs.role)?.[isZh ? "zh" : "en"]}</p>
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
                  <span key={g} className="ui-badge">{GOALS.find((gl) => gl.key === g)?.[isZh ? "zh" : "en"]}</span>
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
            {isZh ? currentStep.titleZh : currentStep.title}
          </h1>
          <p className="text-sm mt-2" style={{ color: "var(--text-secondary)" }}>
            {isZh ? currentStep.subtitleZh : currentStep.subtitle}
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
