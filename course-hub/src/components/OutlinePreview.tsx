"use client";

import { ChevronRight, ChevronDown } from "lucide-react";
import { useState } from "react";
import type { ParsedOutlineNode } from "@/types";
import { useI18n } from "@/lib/i18n";

const TYPE_COLORS: Record<string, string> = {
  week: "var(--accent)",
  chapter: "var(--success)",
  topic: "var(--warning)",
  knowledge_point: "var(--text-muted)",
};

function TreeNode({ node, depth = 0 }: { node: ParsedOutlineNode; depth?: number }) {
  const { t } = useI18n();
  const [expanded, setExpanded] = useState(true);
  const hasChildren = node.children && node.children.length > 0;

  const labelKeys: Record<string, string> = {
    week: "outline.week",
    chapter: "outline.chapter",
    topic: "outline.topic",
    knowledge_point: "outline.knowledgePoint",
  };

  const badgeColor = TYPE_COLORS[node.type] ?? "var(--text-muted)";

  return (
    <div style={{ marginLeft: depth * 20 }}>
      <div
        className="flex items-center gap-2.5 rounded-[14px] px-3 py-2 cursor-pointer select-none transition-colors"
        style={{ backgroundColor: "transparent" }}
        onClick={() => hasChildren && setExpanded(!expanded)}
        onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "var(--bg-muted)")}
        onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "transparent")}
      >
        <span className="shrink-0 w-4 flex items-center justify-center transition-transform" style={{ transform: hasChildren && expanded ? "rotate(90deg)" : "rotate(0deg)" }}>
          {hasChildren ? (
            <ChevronRight size={14} style={{ color: "var(--text-muted)" }} />
          ) : (
            <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: "var(--border-strong)" }} />
          )}
        </span>

        <span
          className="inline-flex items-center rounded-lg px-2 py-0.5 text-[11px]"
          style={{
            fontWeight: 500,
            color: badgeColor,
            backgroundColor: "var(--bg-muted)",
          }}
        >
          {t(labelKeys[node.type] ?? "outline.topic")}
        </span>

        <span className="text-sm" style={{ color: "var(--text-primary)", fontWeight: depth < 2 ? 500 : 400 }}>
          {node.title}
        </span>
      </div>

      {expanded && hasChildren && (
        <div className="mt-0.5">
          {node.children.map((child, i) => (
            <TreeNode key={i} node={child} depth={depth + 1} />
          ))}
        </div>
      )}
    </div>
  );
}

export function OutlinePreview({ nodes }: { nodes: ParsedOutlineNode[] }) {
  return (
    <div className="ui-panel p-5 md:p-6">
      <div className="space-y-0.5">
        {nodes.map((node, i) => (
          <TreeNode key={i} node={node} />
        ))}
      </div>
    </div>
  );
}
