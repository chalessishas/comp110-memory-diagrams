"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { List, BookOpen, BarChart3, NotebookPen, FolderOpen, RotateCcw, PenLine, TreePine } from "lucide-react";
import { useI18n } from "@/lib/i18n";

export function CourseTabs({ courseId }: { courseId: string }) {
  const pathname = usePathname();
  const { t } = useI18n();
  const base = `/course/${courseId}`;

  const tabs = [
    { href: `${base}/learn`, label: t("tabs.learn"), icon: BookOpen },
    { href: `${base}/tree`, label: t("tabs.tree"), icon: TreePine },
    { href: base, label: t("tabs.outline"), icon: List, exact: true },
    { href: `${base}/notes`, label: t("tabs.notes"), icon: NotebookPen },
    { href: `${base}/practice`, label: t("tabs.practice"), icon: PenLine },
    { href: `${base}/progress`, label: t("tabs.progress"), icon: BarChart3 },
    { href: `${base}/library`, label: t("tabs.library"), icon: FolderOpen },
    { href: `${base}/review`, label: t("tabs.review"), icon: RotateCcw },
  ];

  return (
    <div className="ui-tab-row mb-8">
      {tabs.map((tab) => {
        const isActive = tab.exact ? pathname === tab.href : pathname.startsWith(tab.href);
        return (
          <Link
            key={tab.href}
            href={tab.href}
            className={`ui-tab ${isActive ? "ui-tab-active" : ""}`}
          >
            <tab.icon size={16} />
            {tab.label}
          </Link>
        );
      })}
    </div>
  );
}
