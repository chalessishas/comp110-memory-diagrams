"use client";

import { useState, useEffect } from "react";
import { isOnboardingComplete } from "@/lib/onboarding";
import { OnboardingWizard } from "@/components/OnboardingWizard";

export function OnboardingGate({ children }: { children: React.ReactNode }) {
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    if (!isOnboardingComplete()) {
      setShowOnboarding(true);
    }
  }, []);

  // Don't render anything until mounted (avoid hydration mismatch)
  if (!mounted) return <>{children}</>;

  if (showOnboarding) {
    return <OnboardingWizard onComplete={() => setShowOnboarding(false)} />;
  }

  return <>{children}</>;
}
