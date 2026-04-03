"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { List, BookOpen, BarChart3 } from "lucide-react";

export function CourseTabs({ courseId }: { courseId: string }) {
  const pathname = usePathname();
  const base = `/course/${courseId}`;

  const tabs = [
    { href: base, label: "Outline", icon: List, exact: true },
    { href: `${base}/practice`, label: "Practice", icon: BookOpen },
    { href: `${base}/progress`, label: "Progress", icon: BarChart3 },
  ];

  return (
    <div className="flex gap-1 border-b mb-6" style={{ borderColor: "var(--border)" }}>
      {tabs.map((tab) => {
        const isActive = tab.exact ? pathname === tab.href : pathname.startsWith(tab.href);
        return (
          <Link
            key={tab.href}
            href={tab.href}
            className="flex items-center gap-1.5 px-4 py-2.5 text-sm transition-colors -mb-px"
            style={{
              color: isActive ? "var(--text-primary)" : "var(--text-secondary)",
              borderBottom: isActive ? "2px solid var(--accent)" : "2px solid transparent",
              fontWeight: isActive ? 500 : 400,
            }}
          >
            <tab.icon size={16} />
            {tab.label}
          </Link>
        );
      })}
    </div>
  );
}
