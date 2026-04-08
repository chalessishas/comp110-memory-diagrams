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
      <span
        onClick={() => setOpen(!open)}
        className="cursor-pointer border-b border-dotted transition-colors"
        style={{
          borderColor: "var(--accent)",
          color: "inherit",
        }}
      >
        {children}
      </span>

      {open && (
        <div
          ref={popRef}
          className="absolute z-50 px-4 py-3 rounded-xl shadow-lg text-sm max-w-xs"
          style={{
            backgroundColor: "var(--bg-surface)",
            border: "1px solid var(--border)",
            [above ? "bottom" : "top"]: "calc(100% + 6px)",
            left: "50%",
            transform: "translateX(-50%)",
            minWidth: "200px",
          }}
        >
          {/* Arrow */}
          <div
            className="absolute w-2 h-2 rotate-45"
            style={{
              backgroundColor: "var(--bg-surface)",
              borderRight: above ? "1px solid var(--border)" : "none",
              borderBottom: above ? "1px solid var(--border)" : "none",
              borderLeft: above ? "none" : "1px solid var(--border)",
              borderTop: above ? "none" : "1px solid var(--border)",
              [above ? "bottom" : "top"]: "-5px",
              left: "50%",
              transform: "translateX(-50%) rotate(45deg)",
            }}
          />
          <p className="font-semibold text-xs mb-1" style={{ color: "var(--accent)" }}>
            {term.term}
          </p>
          <p className="text-xs leading-relaxed" style={{ color: "var(--text-secondary)" }}>
            {term.definition}
          </p>
        </div>
      )}
    </span>
  );
}
