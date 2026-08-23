"use client";

import { useState } from "react";
import { Copy, Check, FileText, Code2 } from "lucide-react";

interface SarMarkdownViewerProps {
  sarReport: {
    sar_id: string;
    narrative_text: string;
    filing_timestamp?: string;
    suspect_entity?: string;
    summary_of_suspicious_activity?: string;
    recommended_action?: string;
    [key: string]: any;
  };
}

export default function SarMarkdownViewer({ sarReport }: SarMarkdownViewerProps) {
  const [viewMode, setViewMode] = useState<"narrative" | "json">("narrative");
  const [copied, setCopied] = useState<boolean>(false);

  const text = sarReport?.narrative_text || "";

  // Helper to parse basic Markdown lines cleanly
  function renderMarkdown(md: string) {
    const lines = md.split("\n");
    return lines.map((line, idx) => {
      const trimmed = line.trim();

      // Heading 3 / Section Title
      if (trimmed.startsWith("### ")) {
        return (
          <h4 key={idx} className="text-xs font-mono font-bold text-sky-400 mt-2.5 mb-1 tracking-wide uppercase">
            {trimmed.replace(/^###\s+/, "")}
          </h4>
        );
      }

      // Heading 2
      if (trimmed.startsWith("## ")) {
        return (
          <h3 key={idx} className="text-xs font-mono font-bold text-slate-100 mt-3 mb-1 tracking-wide border-b border-[#1C2230] pb-1">
            {trimmed.replace(/^##\s+/, "")}
          </h3>
        );
      }

      // Bullet Point
      if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
        const content = trimmed.replace(/^[-*]\s+/, "");
        return (
          <div key={idx} className="flex items-start gap-1.5 ml-2 my-0.5 text-slate-300 text-[11px]">
            <span className="text-[#FF5F00] font-mono mt-0.5">•</span>
            <span>{formatInline(content)}</span>
          </div>
        );
      }

      // Key-Value style line (e.g. "1. Suspect Entity: ...")
      if (/^\d+\.\s+/.test(trimmed)) {
        return (
          <div key={idx} className="font-mono text-[11px] text-slate-200 mt-2 mb-0.5 font-semibold">
            {formatInline(trimmed)}
          </div>
        );
      }

      // Empty line
      if (!trimmed) {
        return <div key={idx} className="h-1" />;
      }

      // Regular paragraph
      return (
        <p key={idx} className="text-slate-300 text-[11px] leading-relaxed my-0.5">
          {formatInline(trimmed)}
        </p>
      );
    });
  }

  // Format bold text **text** and code `text`
  function formatInline(str: string) {
    const parts = str.split(/(\*\*.*?\*\*|`.*?`)/g);
    return parts.map((part, i) => {
      if (part.startsWith("**") && part.endsWith("**")) {
        return (
          <strong key={i} className="font-semibold text-slate-100">
            {part.slice(2, -2)}
          </strong>
        );
      }
      if (part.startsWith("`") && part.endsWith("`")) {
        return (
          <code key={i} className="font-mono px-1 py-0.5 rounded bg-[#131722] border border-[#232936] text-sky-300 text-[10px]">
            {part.slice(1, -1)}
          </code>
        );
      }
      return part;
    });
  }

  function handleCopy() {
    const payload = viewMode === "json" ? JSON.stringify(sarReport, null, 2) : text;
    navigator.clipboard.writeText(payload);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <div className="terminal-panel flex flex-col bg-[#0B0E14] overflow-hidden">
      {/* Header Bar */}
      <div className="terminal-header">
        <div className="terminal-title text-slate-200">
          <FileText size={13} className="text-emerald-400" />
          <span>FINCEN AUDIT SAR NARRATIVE</span>
          <span className="font-mono text-[10px] text-slate-500">({sarReport?.sar_id})</span>
        </div>

        <div className="flex items-center gap-2">
          {/* Mode Switcher */}
          <div className="flex items-center bg-[#131722] border border-[#1C2230] rounded p-0.5 font-mono text-[9px]">
            <button
              onClick={() => setViewMode("narrative")}
              className={`px-1.5 py-0.5 rounded ${
                viewMode === "narrative" ? "bg-[#1E2536] text-slate-100 font-bold" : "text-slate-500 hover:text-slate-300"
              }`}
            >
              NARRATIVE
            </button>
            <button
              onClick={() => setViewMode("json")}
              className={`px-1.5 py-0.5 rounded ${
                viewMode === "json" ? "bg-[#1E2536] text-slate-100 font-bold" : "text-slate-500 hover:text-slate-300"
              }`}
            >
              JSON
            </button>
          </div>

          <button
            onClick={handleCopy}
            className="btn-subtle py-0.5 px-2 text-[10px] font-mono text-slate-300"
          >
            {copied ? <Check size={11} className="text-emerald-400" /> : <Copy size={11} />}
            <span>{copied ? "COPIED" : "COPY"}</span>
          </button>
        </div>
      </div>

      {/* Content Area */}
      <div className="p-3 font-mono text-xs max-h-56 overflow-y-auto bg-[#08090C]/80">
        {viewMode === "narrative" ? (
          <div className="space-y-0.5">{renderMarkdown(text)}</div>
        ) : (
          <pre className="text-[10px] text-sky-300 whitespace-pre-wrap leading-relaxed">
            {JSON.stringify(sarReport, null, 2)}
          </pre>
        )}
      </div>
    </div>
  );
}
