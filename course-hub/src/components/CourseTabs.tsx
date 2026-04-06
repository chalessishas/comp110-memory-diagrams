"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { CalendarCheck, BookOpen, BarChart3 } from "lucide-react";
import { useI18n } from "@/lib/i18n";

export function CourseTabs({ courseId }: { courseId: string }) {
  const pathname = usePathname();
  const { t } = useI18n();
  const base = `/course/${courseId}`;

  const tabs = [
    { href: base, label: t("tabs.today") || "Today", icon: CalendarCheck, exact: true },
    { href: `${base}/learn`, label: t("tabs.learn") || "Learn", icon: BookOpen },
    { href: `${base}/profile`, label: t("tabs.profile") || "Profile", icon: BarChart3 },
  ];

  return (
    <div className="ui-tab-row mb-6">
      {tabs.map((tab) => {
        const isActive = tab.exact ? pathname === tab.href : pathname.startsWith(tab.href);
        return (
          <Link
            key={tab.href}
            href={tab.href}
            className={`ui-tab ${isActive ? "ui-tab-active" : ""}`}
          >
            <tab.icon size={15} />
            {tab.label}
          </Link>
        );
      })}
    </div>
  );
}
