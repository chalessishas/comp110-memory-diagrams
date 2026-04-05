"use client";

import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from "react";

export type Locale = "en" | "zh";

const translations: Record<Locale, Record<string, string>> = {
  en: {
    // Nav
    "nav.dashboard": "Dashboard",
    "nav.newCourse": "New Course",
    "nav.questionBank": "Question Bank",
    "nav.settings": "Settings",
    "nav.signIn": "Sign In",
    "nav.signOut": "Sign Out",

    // Dashboard
    "dashboard.title": "My Courses",
    "dashboard.subtitle": "All your courses organized in one place.",
    "dashboard.noCourses": "No courses yet",
    "dashboard.uploadToStart": "Upload a syllabus to get started",
    "dashboard.addFirst": "Add Your First Course",
    "dashboard.archived": "Archived Courses",
    "dashboard.guestTitle": "Try CourseHub. No sign-up needed.",
    "dashboard.guestDesc": "Paste a syllabus and see what AI builds for you — course outline, study tasks, and practice questions. Sign in later to save.",
    "dashboard.startGuest": "Start as Guest",
    "dashboard.pasteAny": "Paste any syllabus",
    "dashboard.pasteDesc": "Paste text, get a structured outline instantly.",
    "dashboard.saveReady": "Save when you're ready",
    "dashboard.saveDesc": "Sign in to keep your courses, progress, and practice history.",
    "dashboard.createAnytime": "Create an account anytime",
    "dashboard.createDesc": "No pressure. Use CourseHub freely and create an account whenever you want.",
    "dashboard.studyToday": "How you spent your study time today — solving, reviewing, studying, or idle.",

    // New Course
    "newCourse.title": "Build a course from one file.",
    "newCourse.desc": "Upload a file or paste your syllabus text. AI handles the rest.",
    "newCourse.back": "Back to Dashboard",
    "newCourse.upload": "Upload",
    "newCourse.analyze": "Analyze",
    "newCourse.review": "Review",
    "newCourse.pasteText": "Paste Text",
    "newCourse.uploadFile": "Upload File",
    "newCourse.textInput": "Text Input",
    "newCourse.pasteTitle": "Paste a syllabus, course plan, or class overview.",
    "newCourse.pasteDesc": "Works without an account. Paste any course text and see the outline AI generates.",
    "newCourse.charCount": "characters. Paste at least a short syllabus or course outline to continue.",
    "newCourse.generate": "Generate Preview",
    "newCourse.preview": "Preview",
    "newCourse.checkMap": "Check the course map before creating it.",
    "newCourse.createCourse": "Create Course",
    "newCourse.tryNow": "Try It Now",
    "newCourse.answerNoSignup": "Answer a few questions — no sign-up needed",
    "newCourse.check": "Check",
    "newCourse.missingLow": "This syllabus doesn't have enough detail to build a useful course map.",
    "newCourse.missingMed": "Some information is missing — the outline may be incomplete.",
    "newCourse.missingTip": "Tip: Upload your course schedule, lecture slides, or Canvas module list for a more accurate outline.",

    // Course Tabs
    "tabs.learn": "Learn",
    "tabs.tree": "Tree",
    "tabs.outline": "Outline",
    "tabs.practice": "Practice",
    "tabs.review": "Review",
    "tabs.progress": "Progress",
    "tabs.library": "Library",
    "tabs.notes": "Notes",

    // Learn
    "learn.noLessons": "No lessons yet",
    "learn.generateDesc": "AI will generate a full lesson for each knowledge point in your outline.",
    "learn.generateBtn": "Generate Course Lessons",
    "learn.generating": "Generating lessons...",
    "learn.generatingDesc": "This may take a minute — creating a lesson for each knowledge point.",
    "learn.keyTakeaways": "Key Takeaways",
    "learn.previous": "Previous",
    "learn.next": "Next Lesson",

    // Tree
    "tree.title": "Knowledge Tree",
    "tree.desc": "Watch your understanding grow. Each node represents a concept — it fills up as you learn and practice.",
    "tree.mastered": "Mastered",
    "tree.reviewing": "Reviewing",
    "tree.weak": "Weak",
    "tree.notStarted": "Not started",
    "tree.percentMastered": "mastered",

    // Practice
    "practice.title": "Practice",
    "practice.uploadExam": "Upload Exam",
    "practice.noQuestions": "No practice questions yet",
    "practice.noQuestionsDesc": "Upload a past exam or practice sheet to generate interactive questions",
    "practice.converting": "AI is converting questions...",
    "practice.correct": "Correct",
    "practice.incorrect": "Incorrect",
    "practice.submit": "Submit",
    "practice.answer": "Answer",

    // Progress
    "progress.title": "Knowledge Point Mastery",

    // Library
    "library.title": "Course Library",
    "library.uploadFile": "Upload File",
    "library.noFiles": "No files yet",
    "library.noFilesDesc": "Upload textbooks, slides, past exams — all stored in the cloud",
    "library.extract": "Extract key content with AI",

    // Settings
    "settings.title": "Settings",
    "settings.profile": "Profile",
    "settings.account": "Account",
    "settings.preferences": "Preferences",
    "settings.data": "Data",
    "settings.about": "About",
    "settings.email": "Email",
    "settings.displayName": "Display Name",
    "settings.save": "Save",
    "settings.changePassword": "Change Password",
    "settings.deleteAccount": "Delete Account",
    "settings.deleteWarning": "Permanently delete your account and all associated data. This action cannot be undone.",
    "settings.semester": "Current Semester",
    "settings.aiModel": "AI Model",
    "settings.export": "Export",
    "settings.exportDesc": "Download all your courses, outlines, questions, and progress as a JSON file.",
    "settings.exportAll": "Export All Data",
    "settings.clearLocal": "Clear Local Data",
    "settings.clearLocalDesc": "Study time and review card data is stored in your browser. Clearing it will not affect your courses or questions.",
    "settings.clearStudy": "Clear Study Time",
    "settings.clearReview": "Clear Review Progress",
    "settings.language": "Language",

    // Login
    "login.welcome": "Welcome back.",
    "login.create": "Create your workspace.",
    "login.signInDesc": "Sign in with email or Google to access your courses.",
    "login.createDesc": "Create an account with email and password to get started.",
    "login.signIn": "Sign In",
    "login.createAccount": "Create Account",
    "login.continueGoogle": "Continue with Google",
    "login.bottomNote": "Sign in to save your courses and track progress across devices.",
    "login.continueGuest": "Continue as Guest",

    // Misc
    "misc.loading": "Loading...",
    "misc.error": "Something went wrong",
    "misc.delete": "Delete",
    "misc.cancel": "Cancel",
    "misc.confirm": "Confirm",
  },
  zh: {
    // Nav
    "nav.dashboard": "仪表盘",
    "nav.newCourse": "新建课程",
    "nav.questionBank": "题库",
    "nav.settings": "设置",
    "nav.signIn": "登录",
    "nav.signOut": "退出",

    // Dashboard
    "dashboard.title": "我的课程",
    "dashboard.subtitle": "所有课程，一目了然。",
    "dashboard.noCourses": "还没有课程",
    "dashboard.uploadToStart": "上传课程大纲开始使用",
    "dashboard.addFirst": "添加第一门课程",
    "dashboard.archived": "已归档课程",
    "dashboard.guestTitle": "免注册，直接体验 CourseHub。",
    "dashboard.guestDesc": "粘贴课程大纲，AI 自动生成课程结构、学习任务和练习题。满意后再登录保存。",
    "dashboard.startGuest": "游客体验",
    "dashboard.pasteAny": "粘贴任何大纲",
    "dashboard.pasteDesc": "粘贴文本，立即获得结构化课程大纲。",
    "dashboard.saveReady": "随时保存",
    "dashboard.saveDesc": "登录后保留你的课程、进度和练习记录。",
    "dashboard.createAnytime": "随时创建账号",
    "dashboard.createDesc": "没有压力，先免费使用，想注册时再注册。",
    "dashboard.studyToday": "今天的学习时间分布 — 做题、复习、学习或发呆。",

    // New Course
    "newCourse.title": "一份文件，生成一门课。",
    "newCourse.desc": "上传文件或粘贴大纲文本，AI 搞定剩下的。",
    "newCourse.back": "返回仪表盘",
    "newCourse.upload": "上传",
    "newCourse.analyze": "分析",
    "newCourse.review": "预览",
    "newCourse.pasteText": "粘贴文本",
    "newCourse.uploadFile": "上传文件",
    "newCourse.textInput": "文本输入",
    "newCourse.pasteTitle": "粘贴课程大纲、教学计划或课程简介。",
    "newCourse.pasteDesc": "无需账号即可使用。粘贴任何课程文本，查看 AI 生成的大纲。",
    "newCourse.charCount": "个字符。请至少粘贴一段课程大纲才能继续。",
    "newCourse.generate": "生成预览",
    "newCourse.preview": "预览",
    "newCourse.checkMap": "确认课程结构后再创建。",
    "newCourse.createCourse": "创建课程",
    "newCourse.tryNow": "立即试试",
    "newCourse.answerNoSignup": "做几道题感受一下，无需注册",
    "newCourse.check": "提交",
    "newCourse.missingLow": "这份大纲信息不足，无法生成有效的课程结构。",
    "newCourse.missingMed": "部分信息缺失，大纲可能不完整。",
    "newCourse.missingTip": "建议：上传课程表、课件 PPT 或 Canvas 模块列表，效果更好。",

    // Course Tabs
    "tabs.learn": "学习",
    "tabs.tree": "知识树",
    "tabs.outline": "大纲",
    "tabs.practice": "练习",
    "tabs.review": "复习",
    "tabs.progress": "掌握度",
    "tabs.library": "资料库",
    "tabs.notes": "笔记",

    // Learn
    "learn.noLessons": "还没有课程内容",
    "learn.generateDesc": "AI 将为大纲中的每个知识点生成完整课程。",
    "learn.generateBtn": "生成课程内容",
    "learn.generating": "正在生成课程...",
    "learn.generatingDesc": "可能需要一分钟 — 正在为每个知识点创建课程。",
    "learn.keyTakeaways": "要点总结",
    "learn.previous": "上一课",
    "learn.next": "下一课",

    // Tree
    "tree.title": "知识树",
    "tree.desc": "看着你的知识树生长。每个节点代表一个概念 — 随着学习和练习逐渐长大。",
    "tree.mastered": "已掌握",
    "tree.reviewing": "需复习",
    "tree.weak": "薄弱",
    "tree.notStarted": "未开始",
    "tree.percentMastered": "已掌握",

    // Practice
    "practice.title": "练习",
    "practice.uploadExam": "上传试卷",
    "practice.noQuestions": "还没有练习题",
    "practice.noQuestionsDesc": "上传历年试卷或练习册，AI 自动生成交互式题目",
    "practice.converting": "AI 正在转化题目...",
    "practice.correct": "正确",
    "practice.incorrect": "错误",
    "practice.submit": "提交",
    "practice.answer": "答案",

    // Progress
    "progress.title": "知识点掌握度",

    // Library
    "library.title": "课程资料库",
    "library.uploadFile": "上传文件",
    "library.noFiles": "还没有文件",
    "library.noFilesDesc": "上传教材、课件、试卷 — 全部存在云端",
    "library.extract": "AI 提取核心内容",

    // Settings
    "settings.title": "设置",
    "settings.profile": "个人信息",
    "settings.account": "账号安全",
    "settings.preferences": "偏好设置",
    "settings.data": "数据管理",
    "settings.about": "关于",
    "settings.email": "邮箱",
    "settings.displayName": "显示名称",
    "settings.save": "保存",
    "settings.changePassword": "修改密码",
    "settings.deleteAccount": "删除账号",
    "settings.deleteWarning": "永久删除你的账号和所有数据。此操作不可撤销。",
    "settings.semester": "当前学期",
    "settings.aiModel": "AI 模型",
    "settings.export": "导出",
    "settings.exportDesc": "将所有课程、大纲、题目和学习进度下载为 JSON 文件。",
    "settings.exportAll": "导出全部数据",
    "settings.clearLocal": "清除本地数据",
    "settings.clearLocalDesc": "学习时间和复习卡片数据存储在浏览器中。清除不会影响你的课程和题目。",
    "settings.clearStudy": "清除学习时间",
    "settings.clearReview": "清除复习进度",
    "settings.language": "语言",

    // Login
    "login.welcome": "欢迎回来。",
    "login.create": "创建你的学习空间。",
    "login.signInDesc": "使用邮箱或 Google 登录，访问你的课程。",
    "login.createDesc": "使用邮箱和密码创建账号。",
    "login.signIn": "登录",
    "login.createAccount": "注册",
    "login.continueGoogle": "Google 登录",
    "login.bottomNote": "登录后可跨设备保存课程和学习进度。",
    "login.continueGuest": "游客模式继续",

    // Misc
    "misc.loading": "加载中...",
    "misc.error": "出错了",
    "misc.delete": "删除",
    "misc.cancel": "取消",
    "misc.confirm": "确认",
  },
};

interface I18nContextType {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  t: (key: string) => string;
}

const I18nContext = createContext<I18nContextType>({
  locale: "en",
  setLocale: () => {},
  t: (key) => key,
});

export function I18nProvider({ children }: { children: ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>("en");

  useEffect(() => {
    const saved = localStorage.getItem("coursehub.locale") as Locale | null;
    if (saved && (saved === "en" || saved === "zh")) {
      setLocaleState(saved);
    }
  }, []);

  const setLocale = useCallback((l: Locale) => {
    setLocaleState(l);
    localStorage.setItem("coursehub.locale", l);
  }, []);

  const t = useCallback(
    (key: string) => {
      return translations[locale][key] ?? key;
    },
    [locale]
  );

  return (
    <I18nContext.Provider value={{ locale, setLocale, t }}>
      {children}
    </I18nContext.Provider>
  );
}

export function useI18n() {
  return useContext(I18nContext);
}
