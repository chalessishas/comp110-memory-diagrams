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
    "newCourse.kicker": "New Course",
    "newCourse.step": "Step",
    "newCourse.placeholder": "Example:\nCourse: Introduction to Cognitive Science\nInstructor: Dr. Lee\nWeeks 1-2: Foundations of perception\nWeek 3: Memory systems\nWeek 4: Language processing...",
    "newCourse.outlinePreview": "Outline Preview",
    "newCourse.guestExplore": "You can keep exploring in guest mode. Sign in only when you're ready to save this preview to your dashboard.",
    "newCourse.authSave": "If this looks right, CourseHub will save it and generate supporting study materials.",
    "newCourse.studyPreview": "Study Preview",
    "newCourse.studyPreviewTitle": "What would this course ask you to do?",
    "newCourse.buildingTasks": "Building study tasks from the outline...",
    "newCourse.generatingQuestions": "Generating sample questions...",
    "newCourse.questionPreviewEmpty": "Question preview is not ready yet.",
    "newCourse.guestMode": "Guest Mode",
    "newCourse.guestReady": "Your preview is ready. Open sign in in another tab whenever you want to save it permanently.",
    "newCourse.signInTab": "Sign In in Another Tab",
    "newCourse.tryAnother": "Try Another Input",
    "newCourse.loginToSave": "Log In to Save",
    "newCourse.topSections": "top-level sections",
    "newCourse.savingCourse": "Creating course record...",
    "newCourse.savingOutline": "Saving outline tree...",
    "newCourse.redirecting": "Redirecting to your course...",

    // Generation progress steps
    "gen.step1": "Reading your document...",
    "gen.step2": "Identifying course structure...",
    "gen.step3": "Extracting weekly topics...",
    "gen.step4": "Breaking down knowledge points...",
    "gen.step5": "Mapping prerequisite relationships...",
    "gen.step6": "Building the outline tree...",
    "gen.step7": "Generating study tasks...",
    "gen.step8": "Creating practice questions...",
    "gen.step9": "Almost there — polishing results...",
    "gen.step10": "Finalizing your course...",
    "gen.elapsed": "elapsed",
    "gen.slowWarning": "This is taking longer than usual. Long syllabi with many policies can be slow — hang tight.",

    // Outline type badges
    "outline.week": "Week",
    "outline.chapter": "Chapter",
    "outline.topic": "Topic",
    "outline.knowledgePoint": "Knowledge Point",

    // Course Tabs (v2: 3-view architecture)
    "tabs.today": "Today",
    "tabs.learn": "Learn",
    "tabs.profile": "Profile",
    // "tabs.tree": "Tree",
    // "tabs.outline": "Outline",
    // "tabs.practice": "Practice",
    // "tabs.review": "Review",
    // "tabs.progress": "Progress",
    // "tabs.library": "Library",
    // "tabs.notes": "Notes",

    // Today View
    "today.title": "Today",
    "today.subtitle": "Here's what to focus on right now.",
    "today.allCaughtUp": "You're all caught up!",
    "today.allCaughtUpDesc": "No urgent tasks. You can preview next week's content or review for fun.",
    "today.urgent": "Urgent",
    "today.review": "Review",
    "today.examPrep": "Exam Prep",
    "today.newContent": "New Content",
    "today.weakness": "Weakness",
    "today.startButton": "Start",
    "today.estimatedTime": "min",
    "today.dailyGoal": "Daily Goal",
    "today.completed": "completed",

    // Profile View
    "profile.title": "Mastery Profile",
    "profile.titleZh": "掌握度画像",
    "profile.overview": "Mastery Overview",
    "profile.overviewZh": "掌握度概览",
    "profile.weaknesses": "Persistent Weaknesses",
    "profile.weaknessesZh": "持续性弱点",
    "profile.resolved": "Overcome",
    "profile.resolvedZh": "已克服",
    "profile.metacognition": "Self-assessment Accuracy",
    "profile.metacognitionZh": "元认知准确度",
    "profile.weekSummary": "This Week",
    "profile.weekSummaryZh": "本周学习",

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

    // Review
    "review.title": "Spaced Review",
    "review.due": "due",
    "review.allCaughtUp": "All caught up",
    "review.allCaughtUpDesc": "No questions due for review right now. Keep practicing to build your review queue.",
    "review.howWell": "How well did you know this?",
    "review.again": "Again",
    "review.againDesc": "Forgot completely",
    "review.hard": "Hard",
    "review.hardDesc": "Barely remembered",
    "review.good": "Good",
    "review.goodDesc": "Remembered with effort",
    "review.easy": "Easy",
    "review.easyDesc": "Knew instantly",

    // Study Tasks
    "studyTask.title": "Study Tasks",
    "studyTask.mustKnow": "Must Know",
    "studyTask.shouldKnow": "Should Know",
    "studyTask.niceToKnow": "Nice to Know",
    "studyTask.typeRead": "Read",
    "studyTask.typePractice": "Practice",
    "studyTask.typeReview": "Review",
    "studyTask.progress": "Progress",
    "studyTask.completed": "Completed",

    // Question Card
    "questionCard.multipleChoice": "Multiple Choice",
    "questionCard.trueFalse": "True or False",
    "questionCard.fillBlank": "Fill in the Blank",
    "questionCard.shortAnswer": "Short Answer",
    "questionCard.typeAnswer": "Type your answer...",
    "questionCard.incorrectAnswer": "Incorrect. Correct answer:",
    "questionCard.report": "Report:",
    "questionCard.reportWrong": "Wrong",
    "questionCard.reportUnclear": "Unclear",
    "questionCard.reportTooEasy": "Too Easy",
    "questionCard.reportTooHard": "Too Hard",

    // Exam Countdown
    "exam.upcoming": "Upcoming Exams",
    "exam.noUpcoming": "No upcoming exams. Add one to get adaptive study recommendations.",
    "exam.today": "Today!",
    "exam.tomorrow": "Tomorrow",
    "exam.days": "days",
    "exam.add": "Add",
    "exam.namePlaceholder": "Exam name",

    // Streak Badge
    "streak.dayStreak": "day streak",
    "streak.best": "best:",
    "streak.dailyGoal": "Daily Goal",
    "streak.freezeAvailable": "Streak freeze available",
    "streak.freezeUsed": "Streak freeze used this month",

    // Question Bank
    "bank.title": "Question Bank",
    "bank.subtitle": "Questions you bookmarked across all courses.",
    "bank.noSaved": "No saved questions yet",
    "bank.noSavedDesc": "Bookmark questions while practicing to build your personal bank",
    "bank.answer": "Answer:",

    // Dashboard - Today section
    "dashboard.today": "Today",
    "dashboard.newCourse": "New Course",
    "dashboard.archivedCount": "tucked away for later",

    // Practice extra
    "practice.loadingQuestions": "Loading practice questions...",
    "practice.loadingDesc": "Pulling together the current practice set for this course.",
    "practice.questionOf": "Question",
    "practice.of": "of",
    "practice.uploadExamHide": "Hide Upload",
    "practice.turnMaterial": "Turn material into reps.",
    "practice.workThrough": "Work through generated questions or upload an exam to build a fresh drill set.",

    // Misc
    "misc.loading": "Loading...",
    "misc.error": "Something went wrong",
    "misc.delete": "Delete",
    "misc.cancel": "Cancel",
    "misc.confirm": "Confirm",
    "misc.backToDashboard": "Back to Dashboard",
    "misc.or": "or",
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
    "newCourse.kicker": "新建课程",
    "newCourse.step": "步骤",
    "newCourse.placeholder": "示例：\n课程：认知科学导论\n教授：李博士\n第1-2周：感知基础\n第3周：记忆系统\n第4周：语言处理...",
    "newCourse.outlinePreview": "大纲预览",
    "newCourse.guestExplore": "你可以继续以游客模式浏览。准备保存时再登录。",
    "newCourse.authSave": "确认无误后，CourseHub 将保存课程并生成配套学习资料。",
    "newCourse.studyPreview": "学习预览",
    "newCourse.studyPreviewTitle": "这门课需要你做什么？",
    "newCourse.buildingTasks": "正在从大纲生成学习任务...",
    "newCourse.generatingQuestions": "正在生成示例题目...",
    "newCourse.questionPreviewEmpty": "题目预览尚未就绪。",
    "newCourse.guestMode": "游客模式",
    "newCourse.guestReady": "预览已就绪。随时在新标签页登录以永久保存。",
    "newCourse.signInTab": "在新标签页登录",
    "newCourse.tryAnother": "换一个输入",
    "newCourse.loginToSave": "登录保存",
    "newCourse.topSections": "个顶级章节",
    "newCourse.savingCourse": "正在创建课程...",
    "newCourse.savingOutline": "正在保存大纲...",
    "newCourse.redirecting": "正在跳转到课程页...",

    // Generation progress steps
    "gen.step1": "正在阅读你的文档...",
    "gen.step2": "正在识别课程结构...",
    "gen.step3": "正在提取每周主题...",
    "gen.step4": "正在拆解知识点...",
    "gen.step5": "正在梳理知识前后依赖...",
    "gen.step6": "正在构建大纲树...",
    "gen.step7": "正在生成学习任务...",
    "gen.step8": "正在创建练习题...",
    "gen.step9": "即将完成 — 正在打磨结果...",
    "gen.step10": "正在完成你的课程...",
    "gen.elapsed": "已用时",
    "gen.slowWarning": "这比平时慢一些。内容较多的大纲可能需要更长时间，请耐心等待。",

    // Outline type badges
    "outline.week": "周",
    "outline.chapter": "章",
    "outline.topic": "主题",
    "outline.knowledgePoint": "知识点",

    // Course Tabs (v2: 3-view architecture)
    "tabs.today": "今日任务",
    "tabs.learn": "学习",
    "tabs.profile": "掌握度",
    // "tabs.tree": "知识树",
    // "tabs.outline": "大纲",
    // "tabs.practice": "练习",
    // "tabs.review": "复习",
    // "tabs.progress": "掌握度",
    // "tabs.library": "资料库",
    // "tabs.notes": "笔记",

    // Today View
    "today.title": "今日任务",
    "today.subtitle": "现在该做什么，系统帮你决定。",
    "today.allCaughtUp": "今天状态很好！",
    "today.allCaughtUpDesc": "没有紧急任务。可以提前预习，或者巩固复习。",
    "today.urgent": "紧急",
    "today.review": "复习",
    "today.examPrep": "考前准备",
    "today.newContent": "新内容",
    "today.weakness": "弱点强化",
    "today.startButton": "开始",
    "today.estimatedTime": "分钟",
    "today.dailyGoal": "每日目标",
    "today.completed": "已完成",

    // Profile View
    "profile.title": "Mastery Profile",
    "profile.titleZh": "掌握度画像",
    "profile.overview": "Mastery Overview",
    "profile.overviewZh": "掌握度概览",
    "profile.weaknesses": "Persistent Weaknesses",
    "profile.weaknessesZh": "持续性弱点",
    "profile.resolved": "Overcome",
    "profile.resolvedZh": "已克服",
    "profile.metacognition": "Self-assessment Accuracy",
    "profile.metacognitionZh": "元认知准确度",
    "profile.weekSummary": "This Week",
    "profile.weekSummaryZh": "本周学习",

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

    // Review
    "review.title": "间隔复习",
    "review.due": "待复习",
    "review.allCaughtUp": "全部完成",
    "review.allCaughtUpDesc": "当前没有需要复习的题目，继续练习来积累复习队列。",
    "review.howWell": "你对这道题的掌握程度？",
    "review.again": "再来一次",
    "review.againDesc": "完全忘记了",
    "review.hard": "较难",
    "review.hardDesc": "勉强记住了",
    "review.good": "还好",
    "review.goodDesc": "费力想起来了",
    "review.easy": "很简单",
    "review.easyDesc": "瞬间就知道了",

    // Study Tasks
    "studyTask.title": "学习任务",
    "studyTask.mustKnow": "必须掌握",
    "studyTask.shouldKnow": "应当掌握",
    "studyTask.niceToKnow": "了解即可",
    "studyTask.typeRead": "阅读",
    "studyTask.typePractice": "练习",
    "studyTask.typeReview": "复习",
    "studyTask.progress": "进度",
    "studyTask.completed": "已完成",

    // Question Card
    "questionCard.multipleChoice": "单项选择",
    "questionCard.trueFalse": "判断题",
    "questionCard.fillBlank": "填空题",
    "questionCard.shortAnswer": "简答题",
    "questionCard.typeAnswer": "输入你的答案...",
    "questionCard.incorrectAnswer": "错误。正确答案：",
    "questionCard.report": "反馈：",
    "questionCard.reportWrong": "答案有误",
    "questionCard.reportUnclear": "表述不清",
    "questionCard.reportTooEasy": "太简单",
    "questionCard.reportTooHard": "太难",

    // Exam Countdown
    "exam.upcoming": "即将到来的考试",
    "exam.noUpcoming": "暂无考试计划。添加后可获得自适应学习建议。",
    "exam.today": "今天！",
    "exam.tomorrow": "明天",
    "exam.days": "天",
    "exam.add": "添加",
    "exam.namePlaceholder": "考试名称",

    // Streak Badge
    "streak.dayStreak": "天连续打卡",
    "streak.best": "最高：",
    "streak.dailyGoal": "每日目标",
    "streak.freezeAvailable": "连续打卡保护可用",
    "streak.freezeUsed": "本月已使用连续打卡保护",

    // Question Bank
    "bank.title": "题库",
    "bank.subtitle": "你在所有课程中收藏的题目。",
    "bank.noSaved": "还没有收藏的题目",
    "bank.noSavedDesc": "练习时收藏题目，构建你的专属题库",
    "bank.answer": "答案：",

    // Dashboard - Today section
    "dashboard.today": "今天",
    "dashboard.newCourse": "新建课程",
    "dashboard.archivedCount": "已归档待用",

    // Practice extra
    "practice.loadingQuestions": "加载练习题中...",
    "practice.loadingDesc": "正在整理本课程的练习题。",
    "practice.questionOf": "第",
    "practice.of": "题，共",
    "practice.uploadExamHide": "隐藏上传",
    "practice.turnMaterial": "把课程内容变成练习。",
    "practice.workThrough": "做生成的题目，或上传试卷来创建专项练习集。",

    // Misc
    "misc.loading": "加载中...",
    "misc.error": "出错了",
    "misc.delete": "删除",
    "misc.cancel": "取消",
    "misc.confirm": "确认",
    "misc.backToDashboard": "返回仪表盘",
    "misc.or": "或",
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
