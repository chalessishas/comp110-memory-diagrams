import type { Metadata } from "next";
import "./globals.css";
import { I18nProvider } from "@/lib/i18n";
import { OnboardingGate } from "@/components/OnboardingGate";

export const metadata: Metadata = {
  title: "CourseHub",
  description: "AI-powered course management for students",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <I18nProvider>
          <OnboardingGate>{children}</OnboardingGate>
        </I18nProvider>
      </body>
    </html>
  );
}
