"use client";

import { useMemo } from "react";
import type { MasteryLevel } from "@/types";

interface KnowledgeNodeData {
  id: string;
  title: string;
  mastery: MasteryLevel;
  rate: number;
  totalAttempts: number;
  hasLesson: boolean;
  parentTitle: string | null;
}

interface KnowledgeTreeProps {
  nodes: KnowledgeNodeData[];
  courseId: string;
}

function getNodeStyle(mastery: MasteryLevel) {
  switch (mastery) {
    case "mastered":
      return { size: 56, bg: "#16a34a", border: "#15803d", opacity: 1, label: "Mastered" };
    case "reviewing":
      return { size: 44, bg: "#f59e0b", border: "#d97706", opacity: 1, label: "Reviewing" };
    case "weak":
      return { size: 36, bg: "#ef4444", border: "#dc2626", opacity: 0.9, label: "Weak" };
    default:
      return { size: 24, bg: "var(--border)", border: "var(--border-strong)", opacity: 0.5, label: "Not started" };
  }
}

function NodeCircle({ node, x, y }: { node: KnowledgeNodeData; x: number; y: number }) {
  const style = getNodeStyle(node.mastery);
  const r = style.size / 2;

  return (
    <g className="cursor-pointer" style={{ opacity: style.opacity }}>
      {/* Ring for active nodes */}
      {node.mastery !== "untested" && (
        <circle cx={x} cy={y} r={r + 4} fill="none" stroke={style.bg} strokeWidth={2} opacity={0.3} />
      )}

      {/* Main circle */}
      <circle cx={x} cy={y} r={r} fill={style.bg} stroke={style.border} strokeWidth={2} />

      {/* Progress ring for partial mastery */}
      {(node.mastery === "reviewing" || node.mastery === "weak") && (
        <circle
          cx={x}
          cy={y}
          r={r - 3}
          fill="none"
          stroke="white"
          strokeWidth={2}
          strokeDasharray={`${2 * Math.PI * (r - 3) * node.rate} ${2 * Math.PI * (r - 3)}`}
          strokeLinecap="round"
          transform={`rotate(-90 ${x} ${y})`}
          opacity={0.5}
        />
      )}

      {/* Mastery percentage for active nodes */}
      {node.mastery !== "untested" && (
        <text x={x} y={y + 1} textAnchor="middle" dominantBaseline="central" fill="white" fontSize={r > 18 ? 11 : 9} fontWeight={600}>
          {Math.round(node.rate * 100)}%
        </text>
      )}

      {/* Title below */}
      <text x={x} y={y + r + 14} textAnchor="middle" fontSize={10} fontWeight={500} fill="var(--text-primary)">
        {node.title.length > 18 ? node.title.slice(0, 16) + "..." : node.title}
      </text>

      {/* Mastery label */}
      <text x={x} y={y + r + 26} textAnchor="middle" fontSize={8} fill="var(--text-secondary)">
        {style.label}{node.totalAttempts > 0 ? ` (${node.totalAttempts})` : ""}
      </text>
    </g>
  );
}

export function KnowledgeTree({ nodes }: KnowledgeTreeProps) {
  const layout = useMemo(() => {
    if (nodes.length === 0) return [];

    const cols = Math.ceil(Math.sqrt(nodes.length * 1.5));
    const spacingX = 120;
    const spacingY = 100;
    const offsetX = 80;
    const offsetY = 60;

    return nodes.map((node, i) => {
      const col = i % cols;
      const row = Math.floor(i / cols);
      const jitterX = ((i * 37) % 20) - 10;
      const jitterY = ((i * 53) % 16) - 8;
      return {
        node,
        x: offsetX + col * spacingX + jitterX,
        y: offsetY + row * spacingY + jitterY,
      };
    });
  }, [nodes]);

  if (nodes.length === 0) {
    return (
      <div className="ui-empty">
        <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
          No knowledge points yet. Create a course to grow your tree.
        </p>
      </div>
    );
  }

  const mastered = nodes.filter((n) => n.mastery === "mastered").length;
  const reviewing = nodes.filter((n) => n.mastery === "reviewing").length;
  const weak = nodes.filter((n) => n.mastery === "weak").length;
  const untested = nodes.filter((n) => n.mastery === "untested").length;
  const overallProgress = nodes.length > 0 ? (mastered / nodes.length) * 100 : 0;

  const cols = Math.ceil(Math.sqrt(nodes.length * 1.5));
  const rows = Math.ceil(nodes.length / cols);
  const svgWidth = Math.max(cols * 120 + 100, 400);
  const svgHeight = rows * 100 + 120;

  return (
    <div>
      {/* Stats bar */}
      <div className="flex items-center gap-4 mb-4 flex-wrap">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: "#16a34a" }} />
            <span className="text-xs" style={{ color: "var(--text-secondary)" }}>Mastered ({mastered})</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: "#f59e0b" }} />
            <span className="text-xs" style={{ color: "var(--text-secondary)" }}>Reviewing ({reviewing})</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: "#ef4444" }} />
            <span className="text-xs" style={{ color: "var(--text-secondary)" }}>Weak ({weak})</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: "var(--border)" }} />
            <span className="text-xs" style={{ color: "var(--text-secondary)" }}>Not started ({untested})</span>
          </div>
        </div>
        <div className="flex items-center gap-2 ml-auto">
          <span className="text-xs font-medium">{Math.round(overallProgress)}% mastered</span>
          <div className="w-24 h-2 rounded overflow-hidden" style={{ backgroundColor: "var(--border)" }}>
            <div
              className="h-full rounded"
              style={{ width: `${overallProgress}%`, backgroundColor: "#16a34a", transition: "width 500ms ease" }}
            />
          </div>
        </div>
      </div>

      {/* Tree canvas */}
      <div className="ui-panel p-4 overflow-x-auto">
        <svg width={svgWidth} height={svgHeight} viewBox={`0 0 ${svgWidth} ${svgHeight}`}>
          {/* Dashed connection lines between adjacent nodes */}
          {layout.map((item, i) => {
            if (i === 0) return null;
            const prev = layout[i - 1];
            return (
              <line
                key={`line-${i}`}
                x1={prev.x}
                y1={prev.y}
                x2={item.x}
                y2={item.y}
                stroke="var(--border)"
                strokeWidth={1}
                opacity={0.4}
                strokeDasharray="4 4"
              />
            );
          })}

          {/* Nodes */}
          {layout.map((item) => (
            <NodeCircle key={item.node.id} node={item.node} x={item.x} y={item.y} />
          ))}
        </svg>
      </div>
    </div>
  );
}
