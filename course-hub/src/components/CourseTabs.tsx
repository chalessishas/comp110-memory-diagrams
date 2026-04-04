"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { List, BookOpen, BarChart3, NotebookPen, FolderOpen } from "lucide-react";

export function CourseTabs({ courseId }: { courseId: string }) {
  const pathname = usePathname();
  const base = `/course/${courseId}`;

  const tabs = [
    { href: base, label: "Study", icon: List, exact: true },
    { href: `${base}/notes`, label: "Notes", icon: NotebookPen },
    { href: `${base}/practice`, label: "Practice", icon: BookOpen },
    { href: `${base}/progress`, label: "Progress", icon: BarChart3 },
    { href: `${base}/library`, label: "Library", icon: FolderOpen },
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
