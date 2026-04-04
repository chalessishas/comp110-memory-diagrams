"use client";

import { Tree, type NodeRendererProps } from "react-arborist";
import { ChevronRight, ChevronDown, GripVertical } from "lucide-react";
import type { OutlineNode } from "@/types";

interface TreeNode {
  id: string;
  name: string;
  type: string;
  content: string | null;
  children?: TreeNode[];
}

export function buildTree(nodes: OutlineNode[]): TreeNode[] {
  const map = new Map<string, TreeNode>();
  const roots: TreeNode[] = [];

  for (const node of nodes) {
    map.set(node.id, { id: node.id, name: node.title, type: node.type, content: node.content, children: [] });
  }

  for (const node of nodes) {
    const treeNode = map.get(node.id)!;
    if (node.parent_id && map.has(node.parent_id)) {
      map.get(node.parent_id)!.children!.push(treeNode);
    } else {
      roots.push(treeNode);
    }
  }

  return roots;
}

function Node({ node, style, dragHandle }: NodeRendererProps<TreeNode>) {
  const typeLabel: Record<string, string> = {
    week: "W",
    chapter: "Ch",
    topic: "T",
    knowledge_point: "KP",
  };

  return (
    <div
      style={style}
      ref={dragHandle}
      className="group flex items-center gap-2 rounded-2xl px-3 py-2 cursor-pointer hover:bg-black/5"
      onClick={() => node.toggle()}
    >
      <GripVertical size={12} className="opacity-0 group-hover:opacity-40 shrink-0" style={{ color: "var(--text-secondary)" }} />

      {node.isInternal ? (
        node.isOpen
          ? <ChevronDown size={14} style={{ color: "var(--text-secondary)" }} />
          : <ChevronRight size={14} style={{ color: "var(--text-secondary)" }} />
      ) : (
        <span className="w-3.5 shrink-0" />
      )}

      <span
        className="text-[10px] px-2.5 py-1 rounded-full shrink-0 font-semibold uppercase tracking-[0.18em]"
        style={{ backgroundColor: "var(--bg-muted)", color: "var(--text-secondary)", border: "1px solid var(--border)" }}
      >
        {typeLabel[node.data.type] || "?"}
      </span>

      <span
        className="text-sm truncate"
        style={{ fontWeight: node.level < 2 ? 500 : 400 }}
      >
        {node.data.name}
      </span>
    </div>
  );
}

export function OutlineTree({ nodes }: { nodes: OutlineNode[] }) {
  const treeData = buildTree(nodes);

  if (treeData.length === 0) {
    return (
      <div className="ui-empty">
        <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
          No outline yet. Upload a syllabus to generate one.
        </p>
      </div>
    );
  }

  return (
    <div className="ui-panel p-4 md:p-6">
      <Tree
        data={treeData}
        width="100%"
        height={560}
        indent={26}
        rowHeight={42}
        openByDefault={true}
      >
        {Node}
      </Tree>
    </div>
  );
}
