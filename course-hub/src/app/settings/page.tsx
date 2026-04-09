"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase/client";
import { Loader2, Check } from "lucide-react";
import { useI18n } from "@/lib/i18n";

type Section = "profile" | "account" | "preferences" | "data" | "about";

export default function SettingsPage() {
  const router = useRouter();
  const supabase = createClient();
  const { locale, setLocale, t } = useI18n();
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(true);
  const [activeSection, setActiveSection] = useState<Section>("profile");

  // Profile
  const [displayName, setDisplayName] = useState("");
  const [savingName, setSavingName] = useState(false);
  const [nameSaved, setNameSaved] = useState(false);

  // Account
  const [newPassword, setNewPassword] = useState("");
  const [changingPassword, setChangingPassword] = useState(false);
  const [passwordMessage, setPasswordMessage] = useState<string | null>(null);

  // Preferences
  const [semester, setSemester] = useState("");
  const [savingSemester, setSavingSemester] = useState(false);
  const [semesterSaved, setSemesterSaved] = useState(false);

  // Theme removed

  // Data
  const [exporting, setExporting] = useState(false);
  const [clearing, setClearing] = useState<string | null>(null);

  useEffect(() => {
    supabase.auth.getUser().then(({ data: { user } }) => {
      if (!user) { router.push("/login"); return; }
      setEmail(user.email ?? "");
      setDisplayName(user.user_metadata?.display_name ?? "");
      setSemester(user.user_metadata?.semester ?? "");
      setLoading(false);
    });
  }, []);

  async function handleSaveName() {
    setSavingName(true);
    await supabase.auth.updateUser({ data: { display_name: displayName } });
    setSavingName(false);
    setNameSaved(true);
    setTimeout(() => setNameSaved(false), 2000);
  }

  async function handleChangePassword() {
    if (newPassword.length < 6) return;
    setChangingPassword(true);
    setPasswordMessage(null);
    const { error } = await supabase.auth.updateUser({ password: newPassword });
    if (error) {
      setPasswordMessage(error.message);
    } else {
      setPasswordMessage("Password updated successfully.");
      setNewPassword("");
    }
    setChangingPassword(false);
  }

  async function handleSaveSemester() {
    setSavingSemester(true);
    await supabase.auth.updateUser({ data: { semester } });
    setSavingSemester(false);
    setSemesterSaved(true);
    setTimeout(() => setSemesterSaved(false), 2000);
  }

  async function handleExportData() {
    setExporting(true);
    const [
      { data: courses },
      { data: nodes },
      { data: questions },
      { data: attempts },
      { data: tasks },
      { data: bookmarks },
    ] = await Promise.all([
      supabase.from("courses").select("*"),
      supabase.from("outline_nodes").select("*"),
      supabase.from("questions").select("*"),
      supabase.from("attempts").select("*"),
      supabase.from("study_tasks").select("*"),
      supabase.from("question_bookmarks").select("*"),
    ]);

    const exportData = { exported_at: new Date().toISOString(), courses, outline_nodes: nodes, questions, attempts, study_tasks: tasks, question_bookmarks: bookmarks };
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `coursehub-export-${new Date().toISOString().split("T")[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
    setExporting(false);
  }

  function handleClearStudyTracker() {
    if (!confirm("Clear all study time data? This cannot be undone.")) return;
    setClearing("tracker");
    localStorage.removeItem("coursehub.study-tracker");
    setTimeout(() => setClearing(null), 1000);
  }

  function handleClearReviewCards() {
    if (!confirm("Clear all spaced repetition progress? This cannot be undone.")) return;
    setClearing("review");
    localStorage.removeItem("coursehub.review-cards");
    setTimeout(() => setClearing(null), 1000);
  }

  async function handleDeleteAccount() {
    if (!confirm("Delete your account and ALL data? This cannot be undone.")) return;
    if (!confirm("Are you absolutely sure? All courses, questions, and progress will be permanently deleted.")) return;
    const { data: courses } = await supabase.from("courses").select("id");
    if (courses && courses.length > 0) {
      await supabase.from("courses").delete().in("id", courses.map((c) => c.id));
    }
    await supabase.auth.signOut();
    router.push("/login");
  }

  const sections: { key: Section; label: string }[] = [
    { key: "profile", label: t("settings.profile") },
    { key: "account", label: t("settings.account") },
    { key: "preferences", label: t("settings.preferences") },
    { key: "data", label: t("settings.data") },
    { key: "about", label: t("settings.about") },
  ];

  if (loading) return <div className="p-8"><Loader2 className="animate-spin mx-auto mt-16" /></div>;

  return (
    <div className="max-w-3xl mx-auto py-8 px-4">
      <h1 className="text-3xl font-semibold mb-8">{t("settings.title")}</h1>

      {/* Section nav */}
      <div className="flex gap-1.5 mb-8 overflow-x-auto pb-2">
        {sections.map((s) => (
          <button
            key={s.key}
            onClick={() => setActiveSection(s.key)}
            className={`text-sm cursor-pointer ${activeSection === s.key ? "underline" : ""}`}
          >
            [{s.label}]
          </button>
        ))}
      </div>

      {/* Profile */}
      {activeSection === "profile" && (
        <div className="space-y-6">
          <div className="ui-panel p-6">
            <h2 className="text-lg font-semibold mb-4">{t("settings.profile")}</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium mb-1.5">{t("settings.email")}</label>
                <input value={email} disabled className="w-full px-4 py-2.5 text-sm" />
              </div>
              <div>
                <label className="block text-xs font-medium mb-1.5">{t("settings.displayName")}</label>
                <div className="flex gap-2">
                  <input value={displayName} onChange={(e) => setDisplayName(e.target.value)} placeholder="Your name" className="flex-1 px-4 py-2.5 text-sm outline-none" />
                  <button onClick={handleSaveName} disabled={savingName} className="px-4 py-2.5 text-sm font-medium cursor-pointer disabled:opacity-50">
                    {savingName ? <Loader2 size={14} className="animate-spin" /> : nameSaved ? <Check size={14} /> : t("settings.save")}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Account */}
      {activeSection === "account" && (
        <div className="space-y-6">
          <div className="ui-panel p-6">
            <h2 className="text-lg font-semibold mb-4">{t("settings.changePassword")}</h2>
            <div className="flex gap-2">
              <input type="password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} placeholder="New password (min 6 characters)" minLength={6} className="flex-1 px-4 py-2.5 text-sm outline-none" />
              <button onClick={handleChangePassword} disabled={changingPassword || newPassword.length < 6} className="px-4 py-2.5 text-sm font-medium cursor-pointer disabled:opacity-50">
                {changingPassword ? <Loader2 size={14} className="animate-spin" /> : t("settings.save")}
              </button>
            </div>
            {passwordMessage && <p className="text-xs mt-2">{passwordMessage}</p>}
          </div>

          <div className="ui-panel p-6">
            <h2 className="text-lg font-semibold mb-2">{t("settings.deleteAccount")}</h2>
            <p className="text-sm mb-4">{t("settings.deleteWarning")}</p>
            <button onClick={handleDeleteAccount} className="px-4 py-2.5 text-sm font-medium cursor-pointer">
              ⌫ 
              {t("settings.deleteAccount")}
            </button>
          </div>
        </div>
      )}

      {/* Preferences */}
      {activeSection === "preferences" && (
        <div className="space-y-6">
          <div className="ui-panel p-6">
            <h2 className="text-lg font-semibold mb-4">{t("settings.preferences")}</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium mb-1.5">{t("settings.semester")}</label>
                <div className="flex gap-2">
                  <input value={semester} onChange={(e) => setSemester(e.target.value)} placeholder="e.g. Fall 2026" className="flex-1 px-4 py-2.5 text-sm outline-none" />
                  <button onClick={handleSaveSemester} disabled={savingSemester} className="px-4 py-2.5 text-sm font-medium cursor-pointer disabled:opacity-50">
                    {savingSemester ? <Loader2 size={14} className="animate-spin" /> : semesterSaved ? <Check size={14} /> : t("settings.save")}
                  </button>
                </div>
              </div>
              <div>
                <label className="block text-xs font-medium mb-1.5">{t("settings.aiModel")}</label>
                <input value="Qwen3.5-Plus (DashScope)" disabled className="w-full px-4 py-2.5 text-sm" />
                <p className="text-[10px] mt-1">Model selection is managed by the administrator.</p>
              </div>
              <div>
                <label className="block text-xs font-medium mb-1.5">{t("settings.language")}</label>
                <div className="flex gap-2">
                  <button
                    onClick={() => setLocale("en")}
                    className="px-4 py-2.5 text-sm font-medium cursor-pointer"
                  >
                    English
                  </button>
                  <button
                    onClick={() => setLocale("zh")}
                    className="px-4 py-2.5 text-sm font-medium cursor-pointer"
                  >
                    中文
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Data */}
      {activeSection === "data" && (
        <div className="space-y-6">
          <div className="ui-panel p-6">
            <h2 className="text-lg font-semibold mb-4">{t("settings.export")}</h2>
            <p className="text-sm mb-4">{t("settings.exportDesc")}</p>
            <button onClick={handleExportData} disabled={exporting} className="flex items-center gap-2 px-4 py-2.5 text-sm font-medium cursor-pointer disabled:opacity-50">
              {exporting ? "..." : "[dl]"}
              {t("settings.exportAll")}
            </button>
          </div>

          <div className="ui-panel p-6">
            <h2 className="text-lg font-semibold mb-4">{t("settings.clearLocal")}</h2>
            <p className="text-sm mb-4">{t("settings.clearLocalDesc")}</p>
            <div className="flex flex-wrap gap-2">
              <button onClick={handleClearStudyTracker} disabled={clearing === "tracker"} className="flex items-center gap-2 px-4 py-2.5 text-sm cursor-pointer">
                {clearing === "tracker" ? "[ok]" : "[x]"}
                {t("settings.clearStudy")}
              </button>
              <button onClick={handleClearReviewCards} disabled={clearing === "review"} className="flex items-center gap-2 px-4 py-2.5 text-sm cursor-pointer">
                {clearing === "review" ? "[ok]" : "[x]"}
                {t("settings.clearReview")}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* About */}
      {activeSection === "about" && (
        <div className="ui-panel p-6">
          <h2 className="text-lg font-semibold mb-4">About CourseHub</h2>
          <div className="space-y-3 text-sm">
            <p><span className="font-medium">Version:</span> 1.0.0 (MVP)</p>
            <p><span className="font-medium">Stack:</span> Next.js 16 + Supabase + Qwen AI</p>
            <p><span className="font-medium">AI Model:</span> Qwen3.5-Plus via DashScope</p>
            <p><span className="font-medium">Storage:</span> Supabase (PostgreSQL + Object Storage)</p>
            <p className="pt-3 mt-3">
              CourseHub turns your syllabus into a structured learning system — outlines, study tasks, practice questions, and mastery tracking. Built for students who want to study smarter, not harder.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
