"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase/client";
import { User, Lock, Sliders, Database, Info, Loader2, Check, Trash2, Download, RotateCcw } from "lucide-react";

type Section = "profile" | "account" | "preferences" | "data" | "about";

export default function SettingsPage() {
  const router = useRouter();
  const supabase = createClient();
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

  const sections: { key: Section; label: string; icon: typeof User }[] = [
    { key: "profile", label: "Profile", icon: User },
    { key: "account", label: "Account", icon: Lock },
    { key: "preferences", label: "Preferences", icon: Sliders },
    { key: "data", label: "Data", icon: Database },
    { key: "about", label: "About", icon: Info },
  ];

  if (loading) return <div className="p-8"><Loader2 className="animate-spin mx-auto mt-16" style={{ color: "var(--text-secondary)" }} /></div>;

  return (
    <div className="max-w-3xl mx-auto py-8 px-4">
      <h1 className="text-3xl font-semibold mb-8">Settings</h1>

      {/* Section nav */}
      <div className="flex gap-1 mb-8 overflow-x-auto pb-2">
        {sections.map((s) => (
          <button
            key={s.key}
            onClick={() => setActiveSection(s.key)}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm whitespace-nowrap cursor-pointer transition-colors"
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
            <h2 className="text-lg font-semibold mb-4">Profile</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium mb-1.5" style={{ color: "var(--text-secondary)" }}>Email</label>
                <input value={email} disabled className="w-full px-4 py-2.5 rounded-xl text-sm" style={{ border: "1px solid var(--border)", backgroundColor: "var(--bg-muted)", color: "var(--text-secondary)" }} />
              </div>
              <div>
                <label className="block text-xs font-medium mb-1.5" style={{ color: "var(--text-secondary)" }}>Display Name</label>
                <div className="flex gap-2">
                  <input value={displayName} onChange={(e) => setDisplayName(e.target.value)} placeholder="Your name" className="flex-1 px-4 py-2.5 rounded-xl text-sm outline-none" style={{ border: "1px solid var(--border)", backgroundColor: "var(--bg-muted)" }} />
                  <button onClick={handleSaveName} disabled={savingName} className="px-4 py-2.5 rounded-xl text-sm font-medium cursor-pointer disabled:opacity-50" style={{ backgroundColor: "var(--accent)", color: "white" }}>
                    {savingName ? <Loader2 size={14} className="animate-spin" /> : nameSaved ? <Check size={14} /> : "Save"}
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
            <h2 className="text-lg font-semibold mb-4">Change Password</h2>
            <div className="flex gap-2">
              <input type="password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} placeholder="New password (min 6 characters)" minLength={6} className="flex-1 px-4 py-2.5 rounded-xl text-sm outline-none" style={{ border: "1px solid var(--border)", backgroundColor: "var(--bg-muted)" }} />
              <button onClick={handleChangePassword} disabled={changingPassword || newPassword.length < 6} className="px-4 py-2.5 rounded-xl text-sm font-medium cursor-pointer disabled:opacity-50" style={{ backgroundColor: "var(--accent)", color: "white" }}>
                {changingPassword ? <Loader2 size={14} className="animate-spin" /> : "Update"}
              </button>
            </div>
            {passwordMessage && <p className="text-xs mt-2" style={{ color: passwordMessage.includes("success") ? "var(--success)" : "var(--danger)" }}>{passwordMessage}</p>}
          </div>

          <div className="ui-panel p-6">
            <h2 className="text-lg font-semibold mb-2" style={{ color: "var(--danger)" }}>Delete Account</h2>
            <p className="text-sm mb-4" style={{ color: "var(--text-secondary)" }}>Permanently delete your account and all associated data. This action cannot be undone.</p>
            <button onClick={handleDeleteAccount} className="px-4 py-2.5 rounded-xl text-sm font-medium cursor-pointer" style={{ border: "1px solid var(--danger)", color: "var(--danger)" }}>
              <Trash2 size={14} className="inline mr-1.5" />
              Delete My Account
            </button>
          </div>
        </div>
      )}

      {/* Preferences */}
      {activeSection === "preferences" && (
        <div className="space-y-6">
          <div className="ui-panel p-6">
            <h2 className="text-lg font-semibold mb-4">Preferences</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium mb-1.5" style={{ color: "var(--text-secondary)" }}>Current Semester</label>
                <div className="flex gap-2">
                  <input value={semester} onChange={(e) => setSemester(e.target.value)} placeholder="e.g. Fall 2026" className="flex-1 px-4 py-2.5 rounded-xl text-sm outline-none" style={{ border: "1px solid var(--border)", backgroundColor: "var(--bg-muted)" }} />
                  <button onClick={handleSaveSemester} disabled={savingSemester} className="px-4 py-2.5 rounded-xl text-sm font-medium cursor-pointer disabled:opacity-50" style={{ backgroundColor: "var(--accent)", color: "white" }}>
                    {savingSemester ? <Loader2 size={14} className="animate-spin" /> : semesterSaved ? <Check size={14} /> : "Save"}
                  </button>
                </div>
              </div>
              <div>
                <label className="block text-xs font-medium mb-1.5" style={{ color: "var(--text-secondary)" }}>AI Model</label>
                <input value="Qwen3.5-Plus (DashScope)" disabled className="w-full px-4 py-2.5 rounded-xl text-sm" style={{ border: "1px solid var(--border)", backgroundColor: "var(--bg-muted)", color: "var(--text-secondary)" }} />
                <p className="text-[10px] mt-1" style={{ color: "var(--text-secondary)" }}>Model selection is managed by the administrator.</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Data */}
      {activeSection === "data" && (
        <div className="space-y-6">
          <div className="ui-panel p-6">
            <h2 className="text-lg font-semibold mb-4">Export</h2>
            <p className="text-sm mb-4" style={{ color: "var(--text-secondary)" }}>Download all your courses, outlines, questions, and progress as a JSON file.</p>
            <button onClick={handleExportData} disabled={exporting} className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium cursor-pointer disabled:opacity-50" style={{ backgroundColor: "var(--accent)", color: "white" }}>
              {exporting ? <Loader2 size={14} className="animate-spin" /> : <Download size={14} />}
              Export All Data
            </button>
          </div>

          <div className="ui-panel p-6">
            <h2 className="text-lg font-semibold mb-4">Clear Local Data</h2>
            <p className="text-sm mb-4" style={{ color: "var(--text-secondary)" }}>Study time and review card data is stored in your browser. Clearing it will not affect your courses or questions.</p>
            <div className="flex flex-wrap gap-2">
              <button onClick={handleClearStudyTracker} disabled={clearing === "tracker"} className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm cursor-pointer" style={{ border: "1px solid var(--border)", color: "var(--text-secondary)" }}>
                {clearing === "tracker" ? <Check size={14} style={{ color: "var(--success)" }} /> : <RotateCcw size={14} />}
                Clear Study Time
              </button>
              <button onClick={handleClearReviewCards} disabled={clearing === "review"} className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm cursor-pointer" style={{ border: "1px solid var(--border)", color: "var(--text-secondary)" }}>
                {clearing === "review" ? <Check size={14} style={{ color: "var(--success)" }} /> : <RotateCcw size={14} />}
                Clear Review Progress
              </button>
            </div>
          </div>
        </div>
      )}

      {/* About */}
      {activeSection === "about" && (
        <div className="ui-panel p-6">
          <h2 className="text-lg font-semibold mb-4">About CourseHub</h2>
          <div className="space-y-3 text-sm" style={{ color: "var(--text-secondary)" }}>
            <p><span className="font-medium" style={{ color: "var(--text-primary)" }}>Version:</span> 1.0.0 (MVP)</p>
            <p><span className="font-medium" style={{ color: "var(--text-primary)" }}>Stack:</span> Next.js 16 + Supabase + Qwen AI</p>
            <p><span className="font-medium" style={{ color: "var(--text-primary)" }}>AI Model:</span> Qwen3.5-Plus via DashScope</p>
            <p><span className="font-medium" style={{ color: "var(--text-primary)" }}>Storage:</span> Supabase (PostgreSQL + Object Storage)</p>
            <p className="pt-3" style={{ borderTop: "1px solid var(--border)" }}>
              CourseHub turns your syllabus into a structured learning system — outlines, study tasks, practice questions, and mastery tracking. Built for students who want to study smarter, not harder.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
