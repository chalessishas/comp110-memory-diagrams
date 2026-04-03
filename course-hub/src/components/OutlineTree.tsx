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
      className="flex items-center gap-1 py-1 px-2 rounded group cursor-pointer"
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
        className="text-xs px-1.5 py-0.5 rounded shrink-0"
        style={{ backgroundColor: "var(--bg-primary)", color: "var(--text-secondary)" }}
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
      <p className="text-sm py-8 text-center" style={{ color: "var(--text-secondary)" }}>
        No outline yet. Upload a syllabus to generate one.
      </p>
    );
  }

  return (
    <Tree
      data={treeData}
      width="100%"
      height={600}
      indent={24}
      rowHeight={34}
      openByDefault={true}
    >
      {Node}
    </Tree>
  );
}
