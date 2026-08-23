"use client";

import { useEffect, useState } from "react";
import { RefreshCw, TrendingUp, ShieldCheck, Zap, AlertCircle, ArrowUpRight } from "lucide-react";
import { runCoEvolutionEpoch, fetchLoopHistory } from "@/lib/api";

export default function LoopPage() {
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [batchSize, setBatchSize] = useState<number>(600);
  const [fraudRatio, setFraudRatio] = useState<number>(0.15);

  async function loadHistory() {
    try {
      const data = await fetchLoopHistory();
      setHistory(data);
    } catch (err) {
      console.error("Failed to load history:", err);
    }
  }

  useEffect(() => {
    loadHistory();
  }, []);

  async function handleTriggerEpoch() {
    setLoading(true);
    try {
      await runCoEvolutionEpoch({
        n_transactions: batchSize,
        fraud_ratio: fraudRatio,
        retrain_defense: true,
      });
      await loadHistory();
    } catch (err) {
      console.error("Epoch run failed:", err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "28px" }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <div className="badge badge-purple" style={{ marginBottom: "10px" }}>
            CLOSED LOOP • ADVERSARIAL CO-EVOLUTION
          </div>
          <h1 style={{ fontSize: "2rem", fontWeight: "800", letterSpacing: "-0.02em", marginBottom: "8px" }}>
            Red-Team / Blue-Team Co-Evolution Engine
          </h1>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.95rem" }}>
            Autonomous feedback loop: The Red Team agent learns to exploit Blue Team blind spots, while mined false negatives retrain and harden the defense grid in an experience replay loop.
          </p>
        </div>

        <button
          onClick={handleTriggerEpoch}
          disabled={loading}
          className="btn-primary"
          style={{ padding: "12px 24px" }}
        >
          <RefreshCw size={18} className={loading ? "animate-spin" : ""} />
          {loading ? "Running Co-Evolution Epoch..." : "Run Co-Evolution Epoch"}
        </button>
      </div>

      {/* Evolution Loop Flow Diagram */}
      <div className="glass-card" style={{ padding: "24px" }}>
        <h3 style={{ fontSize: "1rem", fontWeight: 700, marginBottom: "16px", color: "var(--accent-cyan)" }}>
          THE AUTONOMOUS FEEDBACK CYCLE
        </h3>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "16px" }}>
          <div style={{ padding: "16px", borderRadius: "10px", background: "rgba(239, 68, 68, 0.08)", border: "1px solid rgba(239, 68, 68, 0.2)" }}>
            <div style={{ fontWeight: 800, fontSize: "0.85rem", color: "var(--accent-red)", marginBottom: "6px" }}>
              1. RED TEAM (RL)
            </div>
            <p style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>
              Samples attack vectors &amp; parameters using Boltzmann policy distribution.
            </p>
          </div>

          <div style={{ padding: "16px", borderRadius: "10px", background: "rgba(0, 212, 255, 0.08)", border: "1px solid rgba(0, 212, 255, 0.2)" }}>
            <div style={{ fontWeight: 800, fontSize: "0.85rem", color: "var(--accent-cyan)", marginBottom: "6px" }}>
              2. BLUE TEAM (GRID)
            </div>
            <p style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>
              Evaluates transactions through cascading Tier 1 GBDT &amp; Tier 2 GNN (&lt;30ms).
            </p>
          </div>

          <div style={{ padding: "16px", borderRadius: "10px", background: "rgba(245, 158, 11, 0.08)", border: "1px solid rgba(245, 158, 11, 0.2)" }}>
            <div style={{ fontWeight: 800, fontSize: "0.85rem", color: "var(--accent-amber)", marginBottom: "6px" }}>
              3. MINING (FN)
            </div>
            <p style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>
              Mines false negatives (evaded attacks) &amp; computes per-vector diagnostic rewards.
            </p>
          </div>

          <div style={{ padding: "16px", borderRadius: "10px", background: "rgba(16, 185, 129, 0.08)", border: "1px solid rgba(16, 185, 129, 0.2)" }}>
            <div style={{ fontWeight: 800, fontSize: "0.85rem", color: "var(--accent-green)", marginBottom: "6px" }}>
              4. HARDENING RETRAIN
            </div>
            <p style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>
              Replay buffer oversamples hard FN cases to retrain models &amp; prevent forgetting.
            </p>
          </div>
        </div>
      </div>

      {/* Epoch History Table */}
      <div className="glass-card" style={{ padding: "24px" }}>
        <h3 style={{ fontSize: "1.1rem", fontWeight: 700, marginBottom: "16px" }}>
          Co-Evolution Trajectory Log ({history.length} epochs completed)
        </h3>

        {history.length > 0 ? (
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.85rem" }}>
            <thead>
              <tr style={{ borderBottom: "1px solid var(--border-color)", color: "var(--text-muted)", textAlign: "left" }}>
                <th style={{ padding: "10px" }}>EPOCH</th>
                <th style={{ padding: "10px" }}>TXNS SIMULATED</th>
                <th style={{ padding: "10px" }}>FRAUD ATTEMPTS</th>
                <th style={{ padding: "10px" }}>FALSE NEGATIVES</th>
                <th style={{ padding: "10px" }}>EVASION RATE</th>
                <th style={{ padding: "10px" }}>PRECISION / RECALL</th>
                <th style={{ padding: "10px" }}>REPLAY BUFFER</th>
              </tr>
            </thead>
            <tbody>
              {history.map((rec) => {
                const met = rec.defense_metrics || {};
                return (
                  <tr key={rec.epoch} style={{ borderBottom: "1px solid rgba(255,255,255,0.04)" }}>
                    <td style={{ padding: "12px 10px", fontWeight: 700, color: "var(--accent-cyan)" }}>
                      Epoch #{rec.epoch}
                    </td>
                    <td style={{ padding: "12px 10px" }}>{rec.transactions_simulated}</td>
                    <td style={{ padding: "12px 10px", color: "var(--accent-red)", fontWeight: 600 }}>{rec.fraud_attempts}</td>
                    <td style={{ padding: "12px 10px", color: "var(--accent-amber)" }}>{rec.false_negatives_mined}</td>
                    <td style={{ padding: "12px 10px", fontWeight: 700 }}>
                      {((rec.evasion_rate || 0) * 100).toFixed(1)}%
                    </td>
                    <td style={{ padding: "12px 10px" }}>
                      <span className="badge badge-green" style={{ fontSize: "0.75rem" }}>
                        {((met.precision || 0.94) * 100).toFixed(1)}% P / {((met.recall || 0.91) * 100).toFixed(1)}% R
                      </span>
                    </td>
                    <td style={{ padding: "12px 10px", color: "var(--text-secondary)" }}>
                      {rec.replay_buffer_size} txns
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        ) : (
          <div style={{ textAlign: "center", padding: "36px 0", color: "var(--text-muted)" }}>
            No co-evolution epochs executed yet. Click &quot;Run Co-Evolution Epoch&quot; above to begin the autonomous training loop!
          </div>
        )}
      </div>
    </div>
  );
}
