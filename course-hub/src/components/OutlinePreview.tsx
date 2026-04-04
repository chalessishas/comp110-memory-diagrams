"use client";

import { ChevronRight, ChevronDown } from "lucide-react";
import { useState } from "react";
import type { ParsedOutlineNode } from "@/types";

const TYPE_STYLES: Record<string, { label: string; color: string; backgroundColor: string; borderColor: string }> = {
  week: {
    label: "Week",
    color: "var(--text-primary)",
    backgroundColor: "rgba(16, 16, 16, 0.06)",
    borderColor: "var(--border-strong)",
  },
  chapter: {
    label: "Chapter",
    color: "var(--text-primary)",
    backgroundColor: "rgba(16, 16, 16, 0.06)",
    borderColor: "var(--border)",
  },
  topic: {
    label: "Topic",
    color: "var(--text-secondary)",
    backgroundColor: "var(--bg-muted)",
    borderColor: "var(--border)",
  },
  knowledge_point: {
    label: "Point",
    color: "var(--text-muted)",
    backgroundColor: "white",
    borderColor: "var(--border)",
  },
};

function TreeNode({ node, depth = 0 }: { node: ParsedOutlineNode; depth?: number }) {
  const [expanded, setExpanded] = useState(true);
  const hasChildren = node.children && node.children.length > 0;
  const typeStyle = TYPE_STYLES[node.type] ?? TYPE_STYLES.topic;

  return (
    <div style={{ marginLeft: depth * 18 }}>
      <div
        className="flex items-center gap-2 rounded-2xl px-3 py-2 cursor-pointer select-none"
        style={{ backgroundColor: depth === 0 ? "rgba(247, 247, 244, 0.95)" : "transparent" }}
        onClick={() => hasChildren && setExpanded(!expanded)}
      >
        {hasChildren ? (
          expanded ? <ChevronDown size={14} style={{ color: "var(--text-secondary)" }} />
            : <ChevronRight size={14} style={{ color: "var(--text-secondary)" }} />
        ) : (
          <span className="w-3.5" />
        )}
        <span
          className="inline-flex items-center rounded-full px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.18em]"
          style={{
            color: typeStyle.color,
            backgroundColor: typeStyle.backgroundColor,
            border: `1px solid ${typeStyle.borderColor}`,
          }}
        >
          {typeStyle.label}
        </span>
        <span className="text-sm" style={{ color: "var(--text-primary)", fontWeight: depth < 2 ? 600 : 500 }}>
          {node.title}
        </span>
      </div>
      {expanded && hasChildren && node.children.map((child, i) => (
        <TreeNode key={i} node={child} depth={depth + 1} />
      ))}
    </div>
  );
}

export function OutlinePreview({ nodes }: { nodes: ParsedOutlineNode[] }) {
  return (
    <div className="ui-panel p-5 md:p-6">
      {nodes.map((node, i) => (
        <TreeNode key={i} node={node} />
      ))}
    </div>
  );
}
