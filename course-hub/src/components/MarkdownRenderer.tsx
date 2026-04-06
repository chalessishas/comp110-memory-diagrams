"use client";

import { Component, type ReactNode } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import rehypeHighlight from "rehype-highlight";
import "katex/dist/katex.min.css";

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

const mdComponents = {
  h2: ({ children }: { children?: ReactNode }) => <h3 className="text-lg font-semibold mt-6 mb-2">{children}</h3>,
  h3: ({ children }: { children?: ReactNode }) => <h4 className="text-base font-semibold mt-4 mb-1">{children}</h4>,
  p: ({ children }: { children?: ReactNode }) => <p className="text-sm leading-relaxed mb-3">{children}</p>,
  ul: ({ children }: { children?: ReactNode }) => <ul className="text-sm space-y-1 mb-3 ml-4 list-disc">{children}</ul>,
  ol: ({ children }: { children?: ReactNode }) => <ol className="text-sm space-y-1 mb-3 ml-4 list-decimal">{children}</ol>,
  li: ({ children }: { children?: ReactNode }) => <li>{children}</li>,
  code: ({ className, children, ...props }: { className?: string; children?: ReactNode }) => {
    const isBlock = className?.includes("language-");
    if (isBlock) {
      return (
        <pre className="p-4 rounded-xl overflow-x-auto text-xs mb-3" style={{ backgroundColor: "#1a1a2e", color: "#e2e8f0" }}>
          <code className={className} {...props}>{children}</code>
        </pre>
      );
    }
    return (
      <code className="px-1.5 py-0.5 rounded text-xs font-mono" style={{ backgroundColor: "var(--bg-muted)" }}>
        {children}
      </code>
    );
  },
  blockquote: ({ children }: { children?: ReactNode }) => (
    <blockquote className="border-l-3 pl-4 my-3 text-sm" style={{ borderColor: "var(--accent)", color: "var(--text-secondary)" }}>
      {children}
    </blockquote>
  ),
};

function MarkdownWithMath({ content }: { content: string }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm, remarkMath]}
      rehypePlugins={[[rehypeKatex, { throwOnError: false, errorColor: "#cc0000", strict: false }], rehypeHighlight]}
      components={mdComponents}
    >
      {content}
    </ReactMarkdown>
  );
}

function MarkdownPlain({ content }: { content: string }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      rehypePlugins={[rehypeHighlight]}
      components={mdComponents}
    >
      {content}
    </ReactMarkdown>
  );
}

export function MarkdownRenderer({ content }: { content: string }) {
  return (
    <div className="prose-custom">
      <MathErrorBoundary fallback={<MarkdownPlain content={content} />}>
        <MarkdownWithMath content={content} />
      </MathErrorBoundary>
    </div>
  );
}
