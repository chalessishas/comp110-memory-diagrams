"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import rehypeHighlight from "rehype-highlight";
import "katex/dist/katex.min.css";

export function MarkdownRenderer({ content }: { content: string }) {
  return (
    <div className="prose-custom">
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkMath]}
        rehypePlugins={[[rehypeKatex, { throwOnError: false, errorColor: "#cc0000" }], rehypeHighlight]}
        components={{
          h2: ({ children }) => <h3 className="text-lg font-semibold mt-6 mb-2">{children}</h3>,
          h3: ({ children }) => <h4 className="text-base font-semibold mt-4 mb-1">{children}</h4>,
          p: ({ children }) => <p className="text-sm leading-relaxed mb-3">{children}</p>,
          ul: ({ children }) => <ul className="text-sm space-y-1 mb-3 ml-4 list-disc">{children}</ul>,
          ol: ({ children }) => <ol className="text-sm space-y-1 mb-3 ml-4 list-decimal">{children}</ol>,
          li: ({ children }) => <li>{children}</li>,
          code: ({ className, children, ...props }) => {
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
          blockquote: ({ children }) => (
            <blockquote className="border-l-3 pl-4 my-3 text-sm" style={{ borderColor: "var(--accent)", color: "var(--text-secondary)" }}>
              {children}
            </blockquote>
          ),
          table: ({ children }) => (
            <div className="overflow-x-auto mb-3">
              <table className="text-sm w-full" style={{ borderCollapse: "collapse" }}>{children}</table>
            </div>
          ),
          th: ({ children }) => <th className="px-3 py-2 text-left font-medium text-xs" style={{ borderBottom: "2px solid var(--border)" }}>{children}</th>,
          td: ({ children }) => <td className="px-3 py-2 text-sm" style={{ borderBottom: "1px solid var(--border)" }}>{children}</td>,
        }}
      />
    </div>
  );
}
