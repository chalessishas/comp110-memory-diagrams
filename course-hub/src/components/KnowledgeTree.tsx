"use client";

import { useMemo } from "react";
import type { MasteryLevel } from "@/types";
import { useI18n } from "@/lib/i18n";

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
      return { size: 56, bg: "var(--mastery-mastered)", border: "var(--success)", opacity: 1, labelKey: "tree.mastered" };
    case "reviewing":
      return { size: 44, bg: "var(--mastery-practiced)", border: "var(--warning)", opacity: 1, labelKey: "tree.reviewing" };
    case "weak":
      return { size: 36, bg: "var(--mastery-exposed)", border: "var(--danger)", opacity: 0.9, labelKey: "tree.weak" };
    default:
      return { size: 24, bg: "var(--mastery-unseen)", border: "var(--border-strong)", opacity: 0.5, labelKey: "tree.notStarted" };
  }
}

function NodeCircle({ node, x, y }: { node: KnowledgeNodeData; x: number; y: number }) {
  const { t } = useI18n();
  const style = getNodeStyle(node.mastery);
  const r = style.size / 2;

  return (
    <g className="cursor-pointer" style={{ opacity: style.opacity }}>
      {node.mastery !== "untested" && (
        <circle cx={x} cy={y} r={r + 4} fill="none" stroke={style.bg} strokeWidth={1.5} opacity={0.2}>
          {node.mastery === "mastered" && (
            <animate attributeName="r" values={`${r + 2};${r + 6};${r + 2}`} dur="4s" repeatCount="indefinite" />
          )}
          {node.mastery === "mastered" && (
            <animate attributeName="opacity" values="0.2;0.08;0.2" dur="4s" repeatCount="indefinite" />
          )}
        </circle>
      )}

      <circle cx={x} cy={y} r={r} fill={style.bg} stroke={style.border} strokeWidth={1.5} />

      {(node.mastery === "reviewing" || node.mastery === "weak") && (
        <circle
          cx={x}
          cy={y}
          r={r - 3}
          fill="none"
          stroke="var(--bg-surface)"
          strokeWidth={1.5}
          strokeDasharray={`${2 * Math.PI * (r - 3) * node.rate} ${2 * Math.PI * (r - 3)}`}
          strokeLinecap="round"
          transform={`rotate(-90 ${x} ${y})`}
          opacity={0.4}
        />
      )}

      {node.mastery !== "untested" && (
        <text x={x} y={y + 1} textAnchor="middle" dominantBaseline="central" fill="var(--bg-surface)" fontSize={r > 18 ? 11 : 9} fontWeight={500}>
          {Math.round(node.rate * 100)}%
        </text>
      )}

      <text x={x} y={y + r + 14} textAnchor="middle" fontSize={10} fontWeight={400} fill="var(--text-primary)">
        {node.title.length > 18 ? node.title.slice(0, 16) + "..." : node.title}
      </text>

      <text x={x} y={y + r + 26} textAnchor="middle" fontSize={8} fill="var(--text-muted)">
        {t(style.labelKey)}{node.totalAttempts > 0 ? ` (${node.totalAttempts})` : ""}
      </text>
    </g>
  );
}

export function KnowledgeTree({ nodes }: KnowledgeTreeProps) {
  const { t } = useI18n();
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
          {t("tree.noNodes")}
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
      <div className="flex items-center gap-4 mb-4 flex-wrap">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: "var(--mastery-mastered)" }} />
            <span className="text-xs" style={{ color: "var(--text-muted)" }}>{t("tree.mastered")} ({mastered})</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: "var(--mastery-practiced)" }} />
            <span className="text-xs" style={{ color: "var(--text-muted)" }}>{t("tree.reviewing")} ({reviewing})</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: "var(--mastery-exposed)" }} />
            <span className="text-xs" style={{ color: "var(--text-muted)" }}>{t("tree.weak")} ({weak})</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: "var(--mastery-unseen)" }} />
            <span className="text-xs" style={{ color: "var(--text-muted)" }}>{t("tree.notStarted")} ({untested})</span>
          </div>
        </div>
        <div className="flex items-center gap-2 ml-auto">
          <span className="text-xs font-medium" style={{ color: "var(--text-secondary)" }}>{Math.round(overallProgress)}% {t("tree.percentMastered")}</span>
          <div className="ui-progress-track w-24">
            <div
              className="ui-progress-bar"
              style={{ width: `${overallProgress}%`, backgroundColor: "var(--mastery-mastered)", transition: "width 500ms ease" }}
            />
          </div>
        </div>
      </div>

      <div className="ui-panel p-4 overflow-x-auto">
        <svg width={svgWidth} height={svgHeight} viewBox={`0 0 ${svgWidth} ${svgHeight}`}>
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
                opacity={0.3}
                strokeDasharray="4 4"
              />
            );
          })}

          {layout.map((item) => (
            <NodeCircle key={item.node.id} node={item.node} x={item.x} y={item.y} />
          ))}
        </svg>
      </div>
    </div>
  );
}
