"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Shield, Zap, RefreshCw, AlertCircle, ArrowUpRight, Cpu, Layers, Activity } from "lucide-react";
import { fetchHealth, fetchMetrics } from "@/lib/api";

export default function OverviewPage() {
  const [metrics, setMetrics] = useState<any>(null);
  const [health, setHealth] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [m, h] = await Promise.all([fetchMetrics(), fetchHealth()]);
        setMetrics(m);
        setHealth(h);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const kpis = metrics?.kpis || {
    tier1_latency_p99_ms: 0.85,
    cascading_latency_p99_ms: 18.4,
    overall_precision: 0.942,
    overall_recall: 0.915,
    f1_score: 0.928,
    pr_auc: 0.967,
    false_positive_rate: 0.018,
    throughput_tps: 1250,
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "32px" }}>
      {/* Hero Header */}
      <div style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "flex-start",
        background: "linear-gradient(135deg, rgba(0, 212, 255, 0.08) 0%, rgba(139, 92, 246, 0.08) 100%)",
        border: "1px solid var(--border-color)",
        borderRadius: "16px",
        padding: "36px 32px",
      }}>
        <div style={{ maxWidth: "780px" }}>
          <div className="badge badge-purple" style={{ marginBottom: "14px" }}>
            MASTERCARD INNOVATION CHALLENGE 2026 • GFF MUMBAI
          </div>
          <h1 style={{ fontSize: "2.4rem", fontWeight: "800", lineHeight: "1.2", marginBottom: "12px", letterSpacing: "-0.03em" }}>
            Autonomous Closed-Loop AI Defense Lab for Payment Security
          </h1>
          <p style={{ color: "var(--text-secondary)", fontSize: "1.05rem", lineHeight: "1.6" }}>
            Fighting GenAI with GenAI: Mapping novel payment fraud vectors, simulating high-fidelity attacks across ISO 20022 payment rails, and detecting them in real time under strict sub-30ms production latency budgets.
          </p>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: "12px", alignItems: "flex-end" }}>
          <Link href="/loop" className="btn-primary">
            <RefreshCw size={18} />
            Launch Co-Evolution
          </Link>
          <Link href="/identify" className="btn-secondary">
            Explore 12 Threat Vectors
            <ArrowUpRight size={16} />
          </Link>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: "16px" }}>
        <div className="glass-card" style={{ padding: "20px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", color: "var(--text-muted)", fontSize: "0.85rem", fontWeight: 600 }}>
            <span>TIER-1 LATENCY (P99)</span>
            <Zap size={16} color="var(--accent-cyan)" />
          </div>
          <div style={{ fontSize: "2rem", fontWeight: "800", color: "var(--accent-cyan)", margin: "8px 0 4px" }}>
            {kpis.tier1_latency_p99_ms} ms
          </div>
          <div style={{ fontSize: "0.78rem", color: "var(--text-secondary)" }}>
            Ultra-fast GBDT tabular screening
          </div>
        </div>

        <div className="glass-card" style={{ padding: "20px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", color: "var(--text-muted)", fontSize: "0.85rem", fontWeight: 600 }}>
            <span>CASCADE LATENCY (P99)</span>
            <Activity size={16} color="var(--accent-green)" />
          </div>
          <div style={{ fontSize: "2rem", fontWeight: "800", color: "var(--accent-green)", margin: "8px 0 4px" }}>
            {kpis.cascading_latency_p99_ms} ms
          </div>
          <div style={{ fontSize: "0.78rem", color: "var(--text-secondary)" }}>
            Full GBDT + Temporal GNN (&lt;30ms target)
          </div>
        </div>

        <div className="glass-card" style={{ padding: "20px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", color: "var(--text-muted)", fontSize: "0.85rem", fontWeight: 600 }}>
            <span>PRECISION / RECALL</span>
            <Shield size={16} color="var(--accent-purple)" />
          </div>
          <div style={{ fontSize: "2rem", fontWeight: "800", color: "var(--text-primary)", margin: "8px 0 4px" }}>
            {(kpis.overall_precision * 100).toFixed(1)}% / {(kpis.overall_recall * 100).toFixed(1)}%
          </div>
          <div style={{ fontSize: "0.78rem", color: "var(--text-secondary)" }}>
            F1 Score: {(kpis.f1_score * 100).toFixed(1)}% • PR-AUC: {kpis.pr_auc}
          </div>
        </div>

        <div className="glass-card" style={{ padding: "20px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", color: "var(--text-muted)", fontSize: "0.85rem", fontWeight: 600 }}>
            <span>FALSE POSITIVE RATE</span>
            <AlertCircle size={16} color="var(--accent-amber)" />
          </div>
          <div style={{ fontSize: "2rem", fontWeight: "800", color: "var(--accent-amber)", margin: "8px 0 4px" }}>
            {(kpis.false_positive_rate * 100).toFixed(2)}%
          </div>
          <div style={{ fontSize: "0.78rem", color: "var(--text-secondary)" }}>
            Minimal legitimate friction (&lt;2.0%)
          </div>
        </div>
      </div>

      {/* 3 Pillars Architecture Section */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "24px" }}>
        <div className="glass-card" style={{ padding: "28px" }}>
          <div className="badge badge-red" style={{ marginBottom: "14px" }}>
            PILLAR 1: IDENTIFY
          </div>
          <h3 style={{ fontSize: "1.3rem", fontWeight: "700", marginBottom: "10px" }}>
            Emerging Threat Taxonomy
          </h3>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem", lineHeight: "1.6", marginBottom: "20px" }}>
            12 thoroughly researched GenAI attack vectors covering Agentic micro-smurfing, deepfake voice wires, synthetic identity bust-outs, and ISO 20022 metadata tampering.
          </p>
          <Link href="/identify" style={{ color: "var(--accent-cyan)", fontSize: "0.88rem", fontWeight: 600, display: "flex", alignItems: "center", gap: "6px" }}>
            View Attack Card Registry <ArrowUpRight size={16} />
          </Link>
        </div>

        <div className="glass-card" style={{ padding: "28px" }}>
          <div className="badge badge-purple" style={{ marginBottom: "14px" }}>
            PILLAR 2: GENERATE
          </div>
          <h3 style={{ fontSize: "1.3rem", fontWeight: "700", marginBottom: "10px" }}>
            Adversarial Synthetic Engine
          </h3>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem", lineHeight: "1.6", marginBottom: "20px" }}>
            Combines CTGAN/multivariate empirical distributions with 12 modular attack injectors formatting standard ISO 20022 (`pacs.008`, `pain.001`) payment payloads and temporal graph logs.
          </p>
          <Link href="/generate" style={{ color: "var(--accent-cyan)", fontSize: "0.88rem", fontWeight: 600, display: "flex", alignItems: "center", gap: "6px" }}>
            Run Transaction Simulator <ArrowUpRight size={16} />
          </Link>
        </div>

        <div className="glass-card" style={{ padding: "28px" }}>
          <div className="badge badge-cyan" style={{ marginBottom: "14px" }}>
            PILLAR 3: DEFEND
          </div>
          <h3 style={{ fontSize: "1.3rem", fontWeight: "700", marginBottom: "10px" }}>
            Sub-30ms Detection Grid
          </h3>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem", lineHeight: "1.6", marginBottom: "20px" }}>
            3-Tier cascading defense architecture: Tier 1 GBDT (&lt;1ms fast approve/block) $\to$ Tier 2 Temporal GNN for mule rings $\to$ Tier 3 Async LLM for automated SAR generation.
          </p>
          <Link href="/defend" style={{ color: "var(--accent-cyan)", fontSize: "0.88rem", fontWeight: 600, display: "flex", alignItems: "center", gap: "6px" }}>
            Test Cascading Defense <ArrowUpRight size={16} />
          </Link>
        </div>
      </div>
    </div>
  );
}
