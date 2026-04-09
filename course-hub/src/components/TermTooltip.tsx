"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import type { TermDefinition } from "@/types";

interface TermTooltipProps {
  term: TermDefinition;
  children: React.ReactNode;
}

export function TermTooltip({ term, children }: TermTooltipProps) {
  const [open, setOpen] = useState(false);
  const [above, setAbove] = useState(true);
  const ref = useRef<HTMLSpanElement>(null);
  const popRef = useRef<HTMLDivElement>(null);

  // Position popover above or below based on available space
  useEffect(() => {
    if (!open || !ref.current) return;
    const rect = ref.current.getBoundingClientRect();
    setAbove(rect.top > 160);
  }, [open]);

  // Close on outside click
  const handleClickOutside = useCallback((e: MouseEvent) => {
    if (ref.current && !ref.current.contains(e.target as Node) &&
        popRef.current && !popRef.current.contains(e.target as Node)) {
      setOpen(false);
    }
  }, []);

  useEffect(() => {
    if (open) {
      document.addEventListener("mousedown", handleClickOutside);
      return () => document.removeEventListener("mousedown", handleClickOutside);
    }
  }, [open, handleClickOutside]);

  return (
    <span ref={ref} className="relative inline">
      {/* Trigger — dotted underline in accent color */}
      <span
        onClick={() => setOpen(!open)}
        className="cursor-pointer"
      >
        {children}
      </span>

      {/* Popup — bg-surface, , subtle , no border */}
      {open && (
        <div
          ref={popRef}
          className="absolute z-50 px-5 py-4 text-sm max-w-xs"
        >
          {/* Arrow */}
          <div
            className="absolute w-2.5 h-2.5 rotate-45"
          />
          <p className="font-semibold text-xs mb-1.5">
            {term.term}
          </p>
          <p className="text-xs leading-relaxed">
            {term.definition}
          </p>
        </div>
      )}
    </span>
  );
}
