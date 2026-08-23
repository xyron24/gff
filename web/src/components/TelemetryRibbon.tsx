"use client";

import Link from "next/link";
import { 
  Zap, 
  Clock, 
  Shield, 
  Activity, 
  AlertTriangle, 
  Radio, 
  ShieldAlert, 
  ChevronRight 
} from "lucide-react";

interface TelemetryRibbonProps {
  metrics?: {
    tier1_latency_p99_ms?: number;
    cascading_latency_p99_ms?: number;
    overall_precision?: number;
    overall_recall?: number;
    f1_score?: number;
    pr_auc?: number;
    false_positive_rate?: number;
    throughput_tps?: number;
  };
}

export default function TelemetryRibbon({ metrics }: TelemetryRibbonProps) {
  const m = {
    tier1_latency_p99_ms: metrics?.tier1_latency_p99_ms ?? 0.85,
    cascading_latency_p99_ms: metrics?.cascading_latency_p99_ms ?? 18.4,
    overall_precision: metrics?.overall_precision ?? 0.942,
    overall_recall: metrics?.overall_recall ?? 0.915,
    f1_score: metrics?.f1_score ?? 0.928,
    pr_auc: metrics?.pr_auc ?? 0.967,
    false_positive_rate: metrics?.false_positive_rate ?? 0.018,
    throughput_tps: metrics?.throughput_tps ?? 1420,
  };

  return (
    <section className="terminal-panel grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 divide-y sm:divide-y-0 sm:divide-x divide-[#1C2230] text-xs">
      {/* 1. Tier-1 Latency */}
      <div className="p-2.5 sm:p-3 flex flex-col justify-between">
        <div className="flex items-center justify-between text-slate-400 text-[10px] font-mono uppercase tracking-wider">
          <span>TIER-1 LATENCY (P99)</span>
          <Zap size={12} className="text-slate-400" />
        </div>
        <div className="flex items-baseline gap-1 my-1">
          <span className="text-sm font-semibold font-mono text-slate-100">{m.tier1_latency_p99_ms.toFixed(2)}</span>
          <span className="font-mono text-[10px] text-slate-500">ms</span>
        </div>
        <div className="text-[10px] text-emerald-400 font-mono flex items-center gap-1">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
          <span>SUB-MS FAST PATH</span>
        </div>
      </div>

      {/* 2. Cascade Latency */}
      <div className="p-2.5 sm:p-3 flex flex-col justify-between">
        <div className="flex items-center justify-between text-slate-400 text-[10px] font-mono uppercase tracking-wider">
          <span>CASCADE LATENCY (P99)</span>
          <Clock size={12} className="text-slate-400" />
        </div>
        <div className="flex items-baseline gap-1 my-1">
          <span className="text-sm font-semibold font-mono text-slate-100">{m.cascading_latency_p99_ms.toFixed(1)}</span>
          <span className="font-mono text-[10px] text-slate-500">ms</span>
        </div>
        <div className="text-[10px] text-sky-400 font-mono">
          <span>SLA &lt;30MS</span> <span className="text-slate-500">(+61% HDROOM)</span>
        </div>
      </div>

      {/* 3. Precision / Recall */}
      <div className="p-2.5 sm:p-3 flex flex-col justify-between">
        <div className="flex items-center justify-between text-slate-400 text-[10px] font-mono uppercase tracking-wider">
          <span>PRECISION / RECALL</span>
          <Shield size={12} className="text-slate-400" />
        </div>
        <div className="flex items-baseline gap-1 my-1">
          <span className="text-sm font-semibold font-mono text-slate-100">
            {(m.overall_precision * 100).toFixed(1)}% / {(m.overall_recall * 100).toFixed(1)}%
          </span>
        </div>
        <div className="text-[10px] text-slate-400 font-mono">
          F1-SCORE: <span className="text-slate-200 font-semibold font-mono">{(m.f1_score * 100).toFixed(1)}%</span>
        </div>
      </div>

      {/* 4. PR-AUC / ROC-AUC */}
      <div className="p-2.5 sm:p-3 flex flex-col justify-between">
        <div className="flex items-center justify-between text-slate-400 text-[10px] font-mono uppercase tracking-wider">
          <span>PR-AUC / ROC-AUC</span>
          <Activity size={12} className="text-slate-400" />
        </div>
        <div className="flex items-baseline gap-1 my-1">
          <span className="text-sm font-semibold font-mono text-slate-100">{m.pr_auc.toFixed(3)}</span>
          <span className="font-mono text-[10px] text-slate-500">/ 0.981</span>
        </div>
        <div className="text-[10px] text-emerald-400 font-mono">
          HIGH-DISCRIMINATION
        </div>
      </div>

      {/* 5. False Positive Rate */}
      <div className="p-2.5 sm:p-3 flex flex-col justify-between">
        <div className="flex items-center justify-between text-slate-400 text-[10px] font-mono uppercase tracking-wider">
          <span>FALSE POSITIVE RATE</span>
          <AlertTriangle size={12} className="text-slate-400" />
        </div>
        <div className="flex items-baseline gap-1 my-1">
          <span className="text-sm font-semibold font-mono text-amber-400">
            {(m.false_positive_rate * 100).toFixed(2)}%
          </span>
        </div>
        <div className="text-[10px] text-slate-500 font-mono">
          BENCHMARK: &lt;3.00%
        </div>
      </div>

      {/* 6. Throughput */}
      <div className="p-2.5 sm:p-3 flex flex-col justify-between">
        <div className="flex items-center justify-between text-slate-400 text-[10px] font-mono uppercase tracking-wider">
          <span>THROUGHPUT</span>
          <Radio size={12} className="text-slate-400" />
        </div>
        <div className="flex items-baseline gap-1 my-1">
          <span className="text-sm font-semibold font-mono text-slate-100">
            {m.throughput_tps.toLocaleString()}
          </span>
          <span className="font-mono text-[10px] text-slate-500">TPS</span>
        </div>
        <div className="text-[10px] text-slate-400 font-mono">
          PEAK: 2,850 TPS
        </div>
      </div>

      {/* 7. Threat Vectors */}
      <div className="p-2.5 sm:p-3 flex flex-col justify-between bg-[#131722]/50">
        <div className="flex items-center justify-between text-slate-400 text-[10px] font-mono uppercase tracking-wider">
          <span>THREAT MATRIX</span>
          <ShieldAlert size={12} className="text-slate-400" />
        </div>
        <div className="flex items-baseline gap-1 my-1">
          <span className="text-sm font-semibold font-mono text-rose-400">12 / 12</span>
          <span className="font-mono text-[10px] text-slate-500">ACTIVE</span>
        </div>
        <Link href="/identify" className="text-[10px] text-[#FF5F00] font-mono hover:underline flex items-center gap-0.5 font-semibold">
          <span>INSPECT VECTORS</span> <ChevronRight size={10} />
        </Link>
      </div>
    </section>
  );
}
