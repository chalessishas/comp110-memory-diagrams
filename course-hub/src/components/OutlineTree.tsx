"use client";

import { useState, useCallback, useRef } from "react";
import { ChevronRight, ChevronDown, Plus, Trash2, Pencil, Check, X, Loader2, Sparkles } from "lucide-react";
import type { OutlineNode } from "@/types";
import { useI18n } from "@/lib/i18n";

interface TreeNode {
  id: string;
  name: string;
  type: string;
  content: string | null;
  children: TreeNode[];
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
      map.get(node.parent_id)!.children.push(treeNode);
    } else {
      roots.push(treeNode);
    }
  }

  return roots;
}

function EditableNode({
  node,
  depth,
  courseId,
  onUpdate,
  onDelete,
  onAdd,
}: {
  node: TreeNode;
  depth: number;
  courseId: string;
  onUpdate: (id: string, title: string) => void;
  onDelete: (id: string) => void;
  onAdd: (parentId: string) => void;
}) {
  const { t } = useI18n();
  const [expanded, setExpanded] = useState(true);
  const [editing, setEditing] = useState(false);
  const [editValue, setEditValue] = useState(node.name);
  const [saving, setSaving] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const hasChildren = node.children.length > 0;

  const typeLabel: Record<string, string> = {
    week: t("outline.week"),
    chapter: t("outline.chapter"),
    topic: t("outline.topic"),
    knowledge_point: t("outline.knowledgePoint"),
  };

  async function handleSave() {
    if (!editValue.trim() || editValue === node.name) {
      setEditing(false);
      setEditValue(node.name);
      return;
    }
    setSaving(true);
    await fetch(`/api/outline-nodes/${node.id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: editValue.trim() }),
    });
    onUpdate(node.id, editValue.trim());
    setSaving(false);
    setEditing(false);
  }

  function startEdit() {
    setEditing(true);
    setEditValue(node.name);
    setTimeout(() => inputRef.current?.focus(), 50);
  }

  return (
    <div>
      <div
        className="group flex items-center gap-2 rounded-md px-3 py-2 hover:bg-black/5"
        style={{ paddingLeft: `${depth * 24 + 12}px` }}
      >
        {/* Expand/collapse */}
        <button
          onClick={() => setExpanded(!expanded)}
          className="shrink-0 cursor-pointer w-4"
        >
          {hasChildren ? (
            expanded ? <ChevronDown size={14} style={{ color: "var(--text-secondary)" }} />
              : <ChevronRight size={14} style={{ color: "var(--text-secondary)" }} />
          ) : <span className="w-3.5" />}
        </button>

        {/* Type badge */}
        <span
          className="text-[10px] px-2.5 py-1 rounded shrink-0 font-semibold uppercase tracking-[0.18em]"
          style={{ backgroundColor: "var(--bg-muted)", color: "var(--text-secondary)", border: "1px solid var(--border)" }}
        >
          {typeLabel[node.type] || "?"}
        </span>

        {/* Title (editable) */}
        {editing ? (
          <div className="flex items-center gap-1 flex-1">
            <input
              ref={inputRef}
              value={editValue}
              onChange={(e) => setEditValue(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") handleSave();
                if (e.key === "Escape") { setEditing(false); setEditValue(node.name); }
              }}
              className="flex-1 text-sm px-2 py-1 rounded-lg outline-none"
              style={{ border: "1px solid var(--border)", backgroundColor: "var(--bg-muted)" }}
              disabled={saving}
            />
            {saving ? (
              <Loader2 size={14} className="animate-spin" style={{ color: "var(--text-secondary)" }} />
            ) : (
              <>
                <button onClick={handleSave} className="cursor-pointer p-1"><Check size={14} style={{ color: "var(--success)" }} /></button>
                <button onClick={() => { setEditing(false); setEditValue(node.name); }} className="cursor-pointer p-1"><X size={14} style={{ color: "var(--text-secondary)" }} /></button>
              </>
            )}
          </div>
        ) : (
          <span
            className="text-sm truncate flex-1 cursor-pointer"
            style={{ fontWeight: depth < 2 ? 500 : 400 }}
            onDoubleClick={startEdit}
          >
            {node.name}
          </span>
        )}

        {/* Action buttons (visible on hover) */}
        {!editing && (
          <div className="flex items-center gap-0.5 opacity-0 group-hover:opacity-100">
            <button onClick={startEdit} className="p-1 cursor-pointer" title="Rename">
              <Pencil size={13} style={{ color: "var(--text-secondary)" }} />
            </button>
            <button onClick={() => onAdd(node.id)} className="p-1 cursor-pointer" title="Add child">
              <Plus size={13} style={{ color: "var(--text-secondary)" }} />
            </button>
            <button
              onClick={() => {
                const msg = hasChildren
                  ? `Delete "${node.name}" and its ${node.children.length} children?`
                  : `Delete "${node.name}"?`;
                if (confirm(msg)) onDelete(node.id);
              }}
              className="p-1 cursor-pointer"
              title="Delete"
            >
              <Trash2 size={13} style={{ color: "var(--danger)" }} />
            </button>
          </div>
        )}
      </div>

      {/* Children */}
      {expanded && node.children.map((child) => (
        <EditableNode
          key={child.id}
          node={child}
          depth={depth + 1}
          courseId={courseId}
          onUpdate={onUpdate}
          onDelete={onDelete}
          onAdd={onAdd}
        />
      ))}
    </div>
  );
}

export function OutlineTree({ nodes, courseId }: { nodes: OutlineNode[]; courseId: string }) {
  const [localNodes, setLocalNodes] = useState(nodes);
  const [dirty, setDirty] = useState(false);
  const [regenerating, setRegenerating] = useState(false);
  const treeData = buildTree(localNodes);

  const handleUpdate = useCallback((id: string, title: string) => {
    setLocalNodes((prev) => prev.map((n) => n.id === id ? { ...n, title } : n));
    setDirty(true);
  }, []);

  const handleDelete = useCallback(async (id: string) => {
    await fetch(`/api/outline-nodes/${id}`, { method: "DELETE" });
    // Remove node and all descendants
    const toRemove = new Set<string>();
    function collectChildren(nodeId: string) {
      toRemove.add(nodeId);
      localNodes.filter((n) => n.parent_id === nodeId).forEach((n) => collectChildren(n.id));
    }
    collectChildren(id);
    setLocalNodes((prev) => prev.filter((n) => !toRemove.has(n.id)));
    setDirty(true);
  }, [localNodes]);

  const handleAdd = useCallback(async (parentId: string) => {
    const title = prompt("New knowledge point title:");
    if (!title?.trim()) return;

    const res = await fetch("/api/outline-nodes", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ course_id: courseId, parent_id: parentId, title: title.trim(), type: "knowledge_point" }),
    });

    if (res.ok) {
      const newNode = await res.json();
      setLocalNodes((prev) => [...prev, newNode]);
      setDirty(true);
    }
  }, [courseId]);

  async function handleRegenerate() {
    setRegenerating(true);
    await fetch(`/api/courses/${courseId}/generate`, { method: "POST" });
    setRegenerating(false);
    setDirty(false);
    window.location.reload();
  }

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
    <div>
      <div className="ui-panel p-4 md:p-6">
        <div className="flex items-center justify-between mb-3">
          <p className="text-xs" style={{ color: "var(--text-secondary)" }}>
            Double-click to rename. Hover for add/delete.
          </p>
        </div>
        {treeData.map((node) => (
          <EditableNode
            key={node.id}
            node={node}
            depth={0}
            courseId={courseId}
            onUpdate={handleUpdate}
            onDelete={handleDelete}
            onAdd={handleAdd}
          />
        ))}
      </div>

      {dirty && (
        <div className="mt-4 flex items-center gap-3 p-4 rounded-md" style={{ backgroundColor: "var(--bg-muted)", border: "1px solid var(--border)" }}>
          <Sparkles size={16} style={{ color: "var(--text-secondary)" }} />
          <p className="text-sm flex-1" style={{ color: "var(--text-secondary)" }}>
            Outline changed. Regenerate study tasks and practice questions?
          </p>
          <button
            onClick={handleRegenerate}
            disabled={regenerating}
            className="px-4 py-2 rounded-md text-sm font-medium cursor-pointer disabled:opacity-50"
            style={{ backgroundColor: "var(--accent)", color: "white" }}
          >
            {regenerating ? <Loader2 size={14} className="animate-spin" /> : "Regenerate"}
          </button>
        </div>
      )}
    </div>
  );
}
