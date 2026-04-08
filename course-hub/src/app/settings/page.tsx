"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase/client";
import { User, Lock, Sliders, Database, Info, Loader2, Check, Trash2, Download, RotateCcw } from "lucide-react";
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
  const [passwordSuccess, setPasswordSuccess] = useState(false);

  // Preferences
  const [semester, setSemester] = useState("");
  const [savingSemester, setSavingSemester] = useState(false);
  const [semesterSaved, setSemesterSaved] = useState(false);

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
    setPasswordSuccess(false);
    const { error } = await supabase.auth.updateUser({ password: newPassword });
    if (error) {
      setPasswordMessage(error.message);
    } else {
      setPasswordSuccess(true);
      setPasswordMessage(t("settings.passwordSuccess"));
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
    if (!confirm(t("settings.confirmClearStudy"))) return;
    setClearing("tracker");
    localStorage.removeItem("coursehub.study-tracker");
    setTimeout(() => setClearing(null), 1000);
  }

  function handleClearReviewCards() {
    if (!confirm(t("settings.confirmClearReview"))) return;
    setClearing("review");
    localStorage.removeItem("coursehub.review-cards");
    setTimeout(() => setClearing(null), 1000);
  }

  async function handleDeleteAccount() {
    if (!confirm(t("settings.confirmDeleteAccount"))) return;
    if (!confirm(t("settings.confirmDeleteFinal"))) return;
    const { data: courses } = await supabase.from("courses").select("id");
    if (courses && courses.length > 0) {
      await supabase.from("courses").delete().in("id", courses.map((c) => c.id));
    }
    await supabase.auth.signOut();
    router.push("/login");
  }

  const sections: { key: Section; label: string; icon: typeof User }[] = [
    { key: "profile", label: t("settings.profile"), icon: User },
    { key: "account", label: t("settings.account"), icon: Lock },
    { key: "preferences", label: t("settings.preferences"), icon: Sliders },
    { key: "data", label: t("settings.data"), icon: Database },
    { key: "about", label: t("settings.about"), icon: Info },
  ];

  if (loading) return <div className="p-8"><Loader2 className="animate-spin mx-auto mt-16" style={{ color: "var(--text-secondary)" }} /></div>;

  return (
    <div className="max-w-3xl mx-auto py-8 px-4">
      <h1 className="text-3xl font-semibold mb-8">{t("settings.title")}</h1>

      {/* Section nav */}
      <div className="flex gap-1 mb-8 overflow-x-auto pb-2">
        {sections.map((s) => (
          <button
            key={s.key}
            onClick={() => setActiveSection(s.key)}
            className="flex items-center gap-2 px-4 py-2.5 rounded-md text-sm whitespace-nowrap cursor-pointer"
            style={{
              backgroundColor: activeSection === s.key ? "var(--accent)" : "var(--bg-surface)",
              color: activeSection === s.key ? "white" : "var(--text-secondary)",
              border: `1px solid ${activeSection === s.key ? "var(--accent)" : "var(--border)"}`,
              fontWeight: activeSection === s.key ? 600 : 400,
            }}
          >
            <s.icon size={14} />
            {s.label}
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
                <label className="block text-xs font-medium mb-1.5" style={{ color: "var(--text-secondary)" }}>{t("settings.email")}</label>
                <input value={email} disabled className="w-full px-4 py-2.5 rounded-xl text-sm" style={{ border: "1px solid var(--border)", backgroundColor: "var(--bg-muted)", color: "var(--text-secondary)" }} />
              </div>
              <div>
                <label className="block text-xs font-medium mb-1.5" style={{ color: "var(--text-secondary)" }}>{t("settings.displayName")}</label>
                <div className="flex gap-2">
                  <input value={displayName} onChange={(e) => setDisplayName(e.target.value)} placeholder={t("settings.namePlaceholder")} className="flex-1 px-4 py-2.5 rounded-xl text-sm outline-none" style={{ border: "1px solid var(--border)", backgroundColor: "var(--bg-muted)" }} />
                  <button onClick={handleSaveName} disabled={savingName} className="px-4 py-2.5 rounded-xl text-sm font-medium cursor-pointer disabled:opacity-50" style={{ backgroundColor: "var(--accent)", color: "white" }}>
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
              <input type="password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} placeholder={t("settings.passwordPlaceholder")} minLength={6} className="flex-1 px-4 py-2.5 rounded-xl text-sm outline-none" style={{ border: "1px solid var(--border)", backgroundColor: "var(--bg-muted)" }} />
              <button onClick={handleChangePassword} disabled={changingPassword || newPassword.length < 6} className="px-4 py-2.5 rounded-xl text-sm font-medium cursor-pointer disabled:opacity-50" style={{ backgroundColor: "var(--accent)", color: "white" }}>
                {changingPassword ? <Loader2 size={14} className="animate-spin" /> : t("settings.save")}
              </button>
            </div>
            {passwordMessage && <p className="text-xs mt-2" style={{ color: passwordSuccess ? "var(--success)" : "var(--danger)" }}>{passwordMessage}</p>}
          </div>

          <div className="ui-panel p-6">
            <h2 className="text-lg font-semibold mb-2" style={{ color: "var(--danger)" }}>{t("settings.deleteAccount")}</h2>
            <p className="text-sm mb-4" style={{ color: "var(--text-secondary)" }}>{t("settings.deleteWarning")}</p>
            <button onClick={handleDeleteAccount} className="px-4 py-2.5 rounded-xl text-sm font-medium cursor-pointer" style={{ border: "1px solid var(--danger)", color: "var(--danger)" }}>
              <Trash2 size={14} className="inline mr-1.5" />
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
                <label className="block text-xs font-medium mb-1.5" style={{ color: "var(--text-secondary)" }}>{t("settings.semester")}</label>
                <div className="flex gap-2">
                  <input value={semester} onChange={(e) => setSemester(e.target.value)} placeholder={t("settings.semesterPlaceholder")} className="flex-1 px-4 py-2.5 rounded-xl text-sm outline-none" style={{ border: "1px solid var(--border)", backgroundColor: "var(--bg-muted)" }} />
                  <button onClick={handleSaveSemester} disabled={savingSemester} className="px-4 py-2.5 rounded-xl text-sm font-medium cursor-pointer disabled:opacity-50" style={{ backgroundColor: "var(--accent)", color: "white" }}>
                    {savingSemester ? <Loader2 size={14} className="animate-spin" /> : semesterSaved ? <Check size={14} /> : t("settings.save")}
                  </button>
                </div>
              </div>
              <div>
                <label className="block text-xs font-medium mb-1.5" style={{ color: "var(--text-secondary)" }}>{t("settings.aiModel")}</label>
                <input value="Qwen3.5-Plus (DashScope)" disabled className="w-full px-4 py-2.5 rounded-xl text-sm" style={{ border: "1px solid var(--border)", backgroundColor: "var(--bg-muted)", color: "var(--text-secondary)" }} />
                <p className="text-[10px] mt-1" style={{ color: "var(--text-secondary)" }}>{t("settings.aiModelManaged")}</p>
              </div>
              <div>
                <label className="block text-xs font-medium mb-1.5" style={{ color: "var(--text-secondary)" }}>{t("settings.language")}</label>
                <div className="flex gap-2">
                  <button
                    onClick={() => setLocale("en")}
                    className="px-4 py-2.5 rounded-xl text-sm font-medium cursor-pointer"
                    style={{
                      backgroundColor: locale === "en" ? "var(--accent)" : "var(--bg-muted)",
                      color: locale === "en" ? "white" : "var(--text-secondary)",
                      border: `1px solid ${locale === "en" ? "var(--accent)" : "var(--border)"}`,
                    }}
                  >
                    English
                  </button>
                  <button
                    onClick={() => setLocale("zh")}
                    className="px-4 py-2.5 rounded-xl text-sm font-medium cursor-pointer"
                    style={{
                      backgroundColor: locale === "zh" ? "var(--accent)" : "var(--bg-muted)",
                      color: locale === "zh" ? "white" : "var(--text-secondary)",
                      border: `1px solid ${locale === "zh" ? "var(--accent)" : "var(--border)"}`,
                    }}
                  >
                    中文
                  </button>
                </div>
              </div>
              <div>
                <label className="block text-xs font-medium mb-1.5" style={{ color: "var(--text-secondary)" }}>{t("settings.theme")}</label>
                <div className="flex gap-2">
                  {([["light", "Light"], ["dark", "Dark"], ["system", "System"]] as const).map(([value, label]) => {
                    const current = typeof window !== "undefined" ? (localStorage.getItem("coursehub.theme") ?? "system") : "system";
                    return (
                      <button
                        key={value}
                        onClick={() => {
                          localStorage.setItem("coursehub.theme", value);
                          if (value === "dark") document.documentElement.setAttribute("data-theme", "midnight");
                          else document.documentElement.removeAttribute("data-theme");
                          window.location.reload();
                        }}
                        className="px-4 py-2.5 rounded-xl text-sm font-medium cursor-pointer"
                        style={{
                          backgroundColor: current === value ? "var(--accent)" : "var(--bg-muted)",
                          color: current === value ? "white" : "var(--text-secondary)",
                          border: `1px solid ${current === value ? "var(--accent)" : "var(--border)"}`,
                        }}
                      >
                        {label}
                      </button>
                    );
                  })}
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
            <p className="text-sm mb-4" style={{ color: "var(--text-secondary)" }}>{t("settings.exportDesc")}</p>
            <button onClick={handleExportData} disabled={exporting} className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium cursor-pointer disabled:opacity-50" style={{ backgroundColor: "var(--accent)", color: "white" }}>
              {exporting ? <Loader2 size={14} className="animate-spin" /> : <Download size={14} />}
              {t("settings.exportAll")}
            </button>
          </div>

          <div className="ui-panel p-6">
            <h2 className="text-lg font-semibold mb-4">{t("settings.clearLocal")}</h2>
            <p className="text-sm mb-4" style={{ color: "var(--text-secondary)" }}>{t("settings.clearLocalDesc")}</p>
            <div className="flex flex-wrap gap-2">
              <button onClick={handleClearStudyTracker} disabled={clearing === "tracker"} className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm cursor-pointer" style={{ border: "1px solid var(--border)", color: "var(--text-secondary)" }}>
                {clearing === "tracker" ? <Check size={14} style={{ color: "var(--success)" }} /> : <RotateCcw size={14} />}
                {t("settings.clearStudy")}
              </button>
              <button onClick={handleClearReviewCards} disabled={clearing === "review"} className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm cursor-pointer" style={{ border: "1px solid var(--border)", color: "var(--text-secondary)" }}>
                {clearing === "review" ? <Check size={14} style={{ color: "var(--success)" }} /> : <RotateCcw size={14} />}
                {t("settings.clearReview")}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* About */}
      {activeSection === "about" && (
        <div className="ui-panel p-6">
          <h2 className="text-lg font-semibold mb-4">{t("settings.aboutTitle")}</h2>
          <div className="space-y-3 text-sm" style={{ color: "var(--text-secondary)" }}>
            <p><span className="font-medium" style={{ color: "var(--text-primary)" }}>{t("settings.version")}:</span> 1.0.0 (MVP)</p>
            <p><span className="font-medium" style={{ color: "var(--text-primary)" }}>{t("settings.stack")}:</span> Next.js 16 + Supabase + Qwen AI</p>
            <p><span className="font-medium" style={{ color: "var(--text-primary)" }}>{t("settings.aiModel")}:</span> Qwen3.5-Plus via DashScope</p>
            <p><span className="font-medium" style={{ color: "var(--text-primary)" }}>{t("settings.storage")}:</span> Supabase (PostgreSQL + Object Storage)</p>
            <p className="pt-3" style={{ borderTop: "1px solid var(--border)" }}>
              {t("settings.aboutDesc")}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
