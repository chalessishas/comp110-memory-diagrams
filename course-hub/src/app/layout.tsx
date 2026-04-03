import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CourseHub",
  description: "AI-powered course management for students",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
