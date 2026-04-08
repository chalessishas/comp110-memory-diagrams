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
    <html lang="en" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: `(function(){try{var t=localStorage.getItem("coursehub.theme");if(t==="dark")document.documentElement.setAttribute("data-theme","midnight");else if(t==="light")document.documentElement.removeAttribute("data-theme");}catch(e){}})()` }} />
      </head>
      <body>
        <I18nProvider>
          <OnboardingGate>{children}</OnboardingGate>
        </I18nProvider>
      </body>
    </html>
  );
}
