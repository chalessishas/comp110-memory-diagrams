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
    <div className="flex gap-1.5 mb-6 p-1">
      {tabs.map((tab) => {
        const isActive = tab.exact ? pathname === tab.href : pathname.startsWith(tab.href);
        return (
          <Link
            key={tab.href}
            href={tab.href}
            className={`flex items-center gap-2 px-4 py-2 text-sm whitespace-nowrap ${
              isActive ? "font-semibold" : "font-medium"
            }`}
          >
            <tab.icon size={15} strokeWidth={isActive ? 2.2 : 1.8} />
            {tab.label}
          </Link>
        );
      })}
    </div>
  );
}
