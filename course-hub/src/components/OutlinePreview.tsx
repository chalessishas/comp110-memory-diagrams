"use client";

import { ChevronRight, ChevronDown } from "lucide-react";
import { useState } from "react";
import type { ParsedOutlineNode } from "@/types";

function TreeNode({ node, depth = 0 }: { node: ParsedOutlineNode; depth?: number }) {
  const [expanded, setExpanded] = useState(true);
  const hasChildren = node.children && node.children.length > 0;

  const typeColors: Record<string, string> = {
    week: "var(--accent)",
    chapter: "var(--accent)",
    topic: "var(--text-primary)",
    knowledge_point: "var(--text-secondary)",
  };

  return (
    <div style={{ marginLeft: depth * 20 }}>
      <div
        className="flex items-center gap-1 py-1 cursor-pointer select-none"
        onClick={() => hasChildren && setExpanded(!expanded)}
      >
        {hasChildren ? (
          expanded ? <ChevronDown size={14} style={{ color: "var(--text-secondary)" }} />
            : <ChevronRight size={14} style={{ color: "var(--text-secondary)" }} />
        ) : (
          <span className="w-3.5" />
        )}
        <span
          className="text-sm"
          style={{ color: typeColors[node.type] || "var(--text-primary)", fontWeight: depth < 2 ? 500 : 400 }}
        >
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
    <div className="p-4 rounded-xl" style={{ backgroundColor: "var(--bg-surface)", border: "1px solid var(--border)" }}>
      {nodes.map((node, i) => (
        <TreeNode key={i} node={node} />
      ))}
    </div>
  );
}
