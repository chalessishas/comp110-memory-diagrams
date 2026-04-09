"use client";

import { Children, Component, isValidElement, cloneElement, type ReactNode, type ReactElement } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import rehypeHighlight from "rehype-highlight";
import "katex/dist/katex.min.css";
import { TermTooltip } from "./TermTooltip";
import type { TermDefinition } from "@/types";

// Error boundary: if KaTeX crashes, re-render without math plugins
class MathErrorBoundary extends Component<{ children: ReactNode; fallback: ReactNode }, { hasError: boolean }> {
  constructor(props: { children: ReactNode; fallback: ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }
  static getDerivedStateFromError() {
    return { hasError: true };
  }
  render() {
    return this.state.hasError ? this.props.fallback : this.props.children;
  }
}

// Split a text string by term matches, wrapping each match in TermTooltip.
// Terms are sorted longest-first to avoid partial matches ("Taylor series" before "Taylor").
function splitTextByTerms(text: string, terms: TermDefinition[]): ReactNode[] {
  if (terms.length === 0) return [text];

  const sorted = [...terms].sort((a, b) => b.term.length - a.term.length);
  const escaped = sorted.map(t => t.term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));
  const regex = new RegExp(`(${escaped.join("|")})`, "gi");

  const parts = text.split(regex);
  return parts.map((part, i) => {
    const matched = sorted.find(t => t.term.toLowerCase() === part.toLowerCase());
    if (matched) {
      return <TermTooltip key={`t-${i}`} term={matched}>{part}</TermTooltip>;
    }
    return part;
  });
}

// Recursively walk React children, replacing text nodes that contain terms
function highlightTerms(children: ReactNode, terms: TermDefinition[]): ReactNode {
  if (!terms || terms.length === 0) return children;

  return Children.map(children, (child) => {
    if (typeof child === "string") {
      return <>{splitTextByTerms(child, terms)}</>;
    }
    // Don't recurse into code blocks, math elements, or TermTooltip
    if (isValidElement(child)) {
      const el = child as ReactElement<Record<string, unknown>>;
      const type = el.type;
      if (type === "code" || type === "pre" || type === TermTooltip) return child;
      // KaTeX renders <span class="katex"> — don't touch those
      const cn = el.props.className;
      if (typeof cn === "string" && cn.includes("katex")) return child;

      if (el.props.children) {
        return cloneElement(el, { ...el.props }, highlightTerms(el.props.children as ReactNode, terms));
      }
    }
    return child;
  });
}

function buildComponents(terms: TermDefinition[]) {
  const wrap = (node: ReactNode) => terms.length > 0 ? highlightTerms(node, terms) : node;

  return {
    h2: ({ children }: { children?: ReactNode }) => (
      <h3 className="text-lg font-semibold mt-8 mb-3 tracking-wide">{wrap(children)}</h3>
    ),
    h3: ({ children }: { children?: ReactNode }) => (
      <h4 className="text-base font-semibold mt-6 mb-2">{wrap(children)}</h4>
    ),
    p: ({ children }: { children?: ReactNode }) => (
      <p className="text-sm leading-[1.7] mb-4">{wrap(children)}</p>
    ),
    ul: ({ children }: { children?: ReactNode }) => <ul className="text-sm space-y-1.5 mb-4 ml-5 list-disc">{children}</ul>,
    ol: ({ children }: { children?: ReactNode }) => <ol className="text-sm space-y-1.5 mb-4 ml-5 list-decimal">{children}</ol>,
    li: ({ children }: { children?: ReactNode }) => <li className="leading-relaxed">{wrap(children)}</li>,
    a: ({ href, children }: { href?: string; children?: ReactNode }) => (
      <a href={href} className="no-underline hover:underline">{children}</a>
    ),
    code: ({ className, children, ...props }: { className?: string; children?: ReactNode }) => {
      const isBlock = className?.includes("language-");
      if (isBlock) {
        return (
          <pre
            className="p-5 overflow-x-auto text-xs mb-4 leading-relaxed"
          >
            <code className={className} {...props}>{children}</code>
          </pre>
        );
      }
      return (
        <code
          className="px-1.5 py-0.5 text-xs font-mono"
        >
          {children}
        </code>
      );
    },
    blockquote: ({ children }: { children?: ReactNode }) => (
      <blockquote
        className="pl-5 my-4 text-sm"
      >
        {wrap(children)}
      </blockquote>
    ),
  };
}

function MarkdownWithMath({ content, terms }: { content: string; terms: TermDefinition[] }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm, remarkMath]}
      rehypePlugins={[[rehypeKatex, { throwOnError: false, errorColor: "#cc0000", strict: false }], rehypeHighlight]}
      components={buildComponents(terms)}
    >
      {content}
    </ReactMarkdown>
  );
}

function MarkdownPlain({ content, terms }: { content: string; terms: TermDefinition[] }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      rehypePlugins={[rehypeHighlight]}
      components={buildComponents(terms)}
    >
      {content}
    </ReactMarkdown>
  );
}

export function MarkdownRenderer({ content, terms }: { content: string; terms?: TermDefinition[] | null }) {
  const safeTerms = terms ?? [];
  return (
    <div className="prose-custom">
      <MathErrorBoundary fallback={<MarkdownPlain content={content} terms={safeTerms} />}>
        <MarkdownWithMath content={content} terms={safeTerms} />
      </MathErrorBoundary>
    </div>
  );
}
