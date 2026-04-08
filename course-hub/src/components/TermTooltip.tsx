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
        className="cursor-pointer transition-colors"
        style={{
          borderBottom: "1.5px dotted var(--accent)",
          color: "inherit",
        }}
      >
        {children}
      </span>

      {/* Popup — bg-surface, rounded-xl, subtle shadow, no border */}
      {open && (
        <div
          ref={popRef}
          className="absolute z-50 px-5 py-4 rounded-xl text-sm max-w-xs"
          style={{
            backgroundColor: "var(--bg-surface)",
            boxShadow: "0 4px 16px var(--accent-light), 0 1px 4px var(--accent-light)",
            [above ? "bottom" : "top"]: "calc(100% + 8px)",
            left: "50%",
            transform: "translateX(-50%)",
            minWidth: "200px",
          }}
        >
          {/* Arrow */}
          <div
            className="absolute w-2.5 h-2.5 rotate-45"
            style={{
              backgroundColor: "var(--bg-surface)",
              [above ? "bottom" : "top"]: "-5px",
              left: "50%",
              transform: "translateX(-50%) rotate(45deg)",
            }}
          />
          <p className="font-semibold text-xs mb-1.5" style={{ color: "var(--accent)" }}>
            {term.term}
          </p>
          <p className="text-xs leading-relaxed" style={{ color: "var(--text-muted)" }}>
            {term.definition}
          </p>
        </div>
      )}
    </span>
  );
}
