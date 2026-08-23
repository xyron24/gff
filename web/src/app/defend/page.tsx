"use client";

import { useState } from "react";
import { Shield, Zap, FileText, CheckCircle, AlertTriangle, XCircle, ArrowRight, Copy } from "lucide-react";
import { scoreTransaction } from "@/lib/api";

export default function DefendPage() {
  const [amount, setAmount] = useState<number>(495.0);
  const [channel, setChannel] = useState<string>("ONLINE");
  const [sender, setSender] = useState<string>("ACC-000420");
  const [receiver, setReceiver] = useState<string>("MERCH-00088");
  const [mcc, setMcc] = useState<string>("5411");
  const [sessionDuration, setSessionDuration] = useState<number>(4.2);
  const [frictionScore, setFrictionScore] = useState<number>(0.02);
  const [remittanceText, setRemittanceText] = useState<string>("Invoice settlement payment #9921");
  const [generateSar, setGenerateSar] = useState<boolean>(true);

  const [loading, setLoading] = useState<boolean>(false);
  const [detectionResult, setDetectionResult] = useState<any>(null);
  const [copied, setCopied] = useState<boolean>(false);

  async function handleScore() {
    setLoading(true);
    try {
      const payload = {
        transaction: {
          txn_id: `TXN-MANUAL-${Math.floor(Math.random() * 900000 + 100000)}`,
          timestamp: new Date().toISOString(),
          sender_account: sender,
          receiver_account: receiver,
          amount: amount,
          channel: channel,
          mcc: mcc,
          session_duration_sec: sessionDuration,
          biometric_friction_score: frictionScore,
          remittance_info: remittanceText,
          is_foreign_transaction: channel === "WIRE",
        },
        generate_sar: generateSar,
      };

      const res = await scoreTransaction(payload);
      setDetectionResult(res);
    } catch (err) {
      console.error("Score failed:", err);
    } finally {
      setLoading(false);
    }
  }

  function handlePreset(type: string) {
    if (type === "smurf") {
      setAmount(195.50);
      setChannel("ONLINE");
      setMcc("4829");
      setSessionDuration(15.0);
      setFrictionScore(0.12);
      setRemittanceText("P2P transfer split");
    } else if (type === "ato") {
      setAmount(18500.0);
      setChannel("API");
      setMcc("4829");
      setSessionDuration(3.2);
      setFrictionScore(0.015);
      setRemittanceText("Instant balance transfer");
    } else if (type === "legit") {
      setAmount(45.0);
      setChannel("POS");
      setMcc("5411");
      setSessionDuration(42.0);
      setFrictionScore(0.035);
      setRemittanceText("Grocery checkout store #102");
    }
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "28px" }}>
      {/* Header */}
      <div>
        <div className="badge badge-cyan" style={{ marginBottom: "10px" }}>
          PILLAR 3 • DEFENSE GRID
        </div>
        <h1 style={{ fontSize: "2rem", fontWeight: "800", letterSpacing: "-0.02em", marginBottom: "8px" }}>
          Cascading Multi-Tier Detection Engine & Automated SAR
        </h1>
        <p style={{ color: "var(--text-secondary)", fontSize: "0.95rem" }}>
          Sub-30ms production authorization grid: Fast tabular GBDT (&lt;1ms) $\to$ Temporal GNN relational analysis $\to$ Cognitive SAR generation.
        </p>
      </div>

      {/* Preset Buttons */}
      <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
        <span style={{ fontSize: "0.82rem", color: "var(--text-muted)", fontWeight: 600 }}>LOAD ATTACK PRESET:</span>
        <button onClick={() => handlePreset("smurf")} className="btn-secondary" style={{ fontSize: "0.8rem", padding: "6px 12px" }}>
          ATK-001 Micro-Smurfing
        </button>
        <button onClick={() => handlePreset("ato")} className="btn-secondary" style={{ fontSize: "0.8rem", padding: "6px 12px" }}>
          ATK-012 Fast Session ATO
        </button>
        <button onClick={() => handlePreset("legit")} className="btn-secondary" style={{ fontSize: "0.8rem", padding: "6px 12px" }}>
          Legitimate Retail Transaction
        </button>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1.1fr 1.3fr", gap: "24px" }}>
        {/* Transaction Input Form */}
        <div className="glass-card" style={{ padding: "28px" }}>
          <h3 style={{ fontSize: "1.15rem", fontWeight: 700, marginBottom: "20px" }}>
            Payment Switch Authorization Simulator
          </h3>

          <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "14px" }}>
              <div>
                <label style={{ fontSize: "0.8rem", color: "var(--text-muted)", fontWeight: 600, display: "block", marginBottom: "6px" }}>
                  TRANSACTION AMOUNT ($)
                </label>
                <input
                  type="number"
                  value={amount}
                  onChange={(e) => setAmount(parseFloat(e.target.value) || 0)}
                  style={{
                    width: "100%",
                    padding: "10px 12px",
                    borderRadius: "8px",
                    background: "rgba(255, 255, 255, 0.04)",
                    border: "1px solid var(--border-color)",
                    color: "var(--text-primary)",
                    fontSize: "0.9rem",
                    outline: "none",
                  }}
                />
              </div>

              <div>
                <label style={{ fontSize: "0.8rem", color: "var(--text-muted)", fontWeight: 600, display: "block", marginBottom: "6px" }}>
                  PAYMENT CHANNEL / RAIL
                </label>
                <select
                  value={channel}
                  onChange={(e) => setChannel(e.target.value)}
                  style={{
                    width: "100%",
                    padding: "10px 12px",
                    borderRadius: "8px",
                    background: "rgba(255, 255, 255, 0.04)",
                    border: "1px solid var(--border-color)",
                    color: "var(--text-primary)",
                    fontSize: "0.9rem",
                    outline: "none",
                  }}
                >
                  <option value="ONLINE">ONLINE (Card-Not-Present)</option>
                  <option value="POS">POS (Point of Sale)</option>
                  <option value="WIRE">WIRE / SWIFT RTGS</option>
                  <option value="P2P">P2P Real-Time</option>
                  <option value="API">Open Banking API (PISP)</option>
                </select>
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "14px" }}>
              <div>
                <label style={{ fontSize: "0.8rem", color: "var(--text-muted)", fontWeight: 600, display: "block", marginBottom: "6px" }}>
                  ORIGINATOR ACCOUNT
                </label>
                <input
                  type="text"
                  value={sender}
                  onChange={(e) => setSender(e.target.value)}
                  style={{
                    width: "100%",
                    padding: "10px 12px",
                    borderRadius: "8px",
                    background: "rgba(255, 255, 255, 0.04)",
                    border: "1px solid var(--border-color)",
                    color: "var(--text-primary)",
                    fontSize: "0.9rem",
                    outline: "none",
                  }}
                />
              </div>

              <div>
                <label style={{ fontSize: "0.8rem", color: "var(--text-muted)", fontWeight: 600, display: "block", marginBottom: "6px" }}>
                  BENEFICIARY ACCOUNT
                </label>
                <input
                  type="text"
                  value={receiver}
                  onChange={(e) => setReceiver(e.target.value)}
                  style={{
                    width: "100%",
                    padding: "10px 12px",
                    borderRadius: "8px",
                    background: "rgba(255, 255, 255, 0.04)",
                    border: "1px solid var(--border-color)",
                    color: "var(--text-primary)",
                    fontSize: "0.9rem",
                    outline: "none",
                  }}
                />
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "14px" }}>
              <div>
                <label style={{ fontSize: "0.8rem", color: "var(--text-muted)", fontWeight: 600, display: "block", marginBottom: "6px" }}>
                  SESSION DURATION ({sessionDuration}s)
                </label>
                <input
                  type="number"
                  step="0.5"
                  value={sessionDuration}
                  onChange={(e) => setSessionDuration(parseFloat(e.target.value) || 0)}
                  style={{
                    width: "100%",
                    padding: "10px 12px",
                    borderRadius: "8px",
                    background: "rgba(255, 255, 255, 0.04)",
                    border: "1px solid var(--border-color)",
                    color: "var(--text-primary)",
                    fontSize: "0.9rem",
                    outline: "none",
                  }}
                />
              </div>

              <div>
                <label style={{ fontSize: "0.8rem", color: "var(--text-muted)", fontWeight: 600, display: "block", marginBottom: "6px" }}>
                  BIOMETRIC FRICTION ({frictionScore})
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  max="1"
                  value={frictionScore}
                  onChange={(e) => setFrictionScore(parseFloat(e.target.value) || 0)}
                  style={{
                    width: "100%",
                    padding: "10px 12px",
                    borderRadius: "8px",
                    background: "rgba(255, 255, 255, 0.04)",
                    border: "1px solid var(--border-color)",
                    color: "var(--text-primary)",
                    fontSize: "0.9rem",
                    outline: "none",
                  }}
                />
              </div>
            </div>

            <div>
              <label style={{ fontSize: "0.8rem", color: "var(--text-muted)", fontWeight: 600, display: "block", marginBottom: "6px" }}>
                ISO 20022 REMITTANCE TEXT
              </label>
              <input
                type="text"
                value={remittanceText}
                onChange={(e) => setRemittanceText(e.target.value)}
                style={{
                  width: "100%",
                  padding: "10px 12px",
                  borderRadius: "8px",
                  background: "rgba(255, 255, 255, 0.04)",
                  border: "1px solid var(--border-color)",
                  color: "var(--text-primary)",
                  fontSize: "0.9rem",
                  outline: "none",
                }}
              />
            </div>

            <button
              onClick={handleScore}
              disabled={loading}
              className="btn-primary"
              style={{ width: "100%", justifyContent: "center", marginTop: "8px" }}
            >
              <Zap size={18} />
              {loading ? "Evaluating in Real-Time..." : "Execute Real-Time Fraud Screening"}
            </button>
          </div>
        </div>

        {/* Results & Cascading Tier Inspector */}
        <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
          {detectionResult ? (
            <>
              {/* Decision Badge Card */}
              <div
                className="glass-card"
                style={{
                  padding: "24px",
                  borderLeft: `6px solid ${
                    detectionResult.decision === "BLOCK"
                      ? "var(--accent-red)"
                      : detectionResult.decision === "CHALLENGE"
                      ? "var(--accent-amber)"
                      : "var(--accent-green)"
                  }`,
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                    {detectionResult.decision === "BLOCK" ? (
                      <XCircle size={28} color="var(--accent-red)" />
                    ) : detectionResult.decision === "CHALLENGE" ? (
                      <AlertTriangle size={28} color="var(--accent-amber)" />
                    ) : (
                      <CheckCircle size={28} color="var(--accent-green)" />
                    )}
                    <div>
                      <div style={{ fontSize: "1.4rem", fontWeight: 800, letterSpacing: "-0.02em" }}>
                        DECISION: {detectionResult.decision}
                      </div>
                      <div style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>
                        Composite Risk Score: {(detectionResult.risk_score * 100).toFixed(1)}%
                      </div>
                    </div>
                  </div>

                  <div className="badge badge-cyan" style={{ fontSize: "0.82rem" }}>
                    {detectionResult.total_latency_ms} MS
                  </div>
                </div>

                {/* Tier Cascade Breakdown */}
                <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "12px", marginTop: "16px" }}>
                  <div style={{ padding: "12px", background: "rgba(255,255,255,0.03)", borderRadius: "8px" }}>
                    <div style={{ fontSize: "0.72rem", color: "var(--text-muted)", fontWeight: 700 }}>TIER 1 (GBDT)</div>
                    <div style={{ fontSize: "1.1rem", fontWeight: 800, color: "var(--accent-cyan)", margin: "4px 0" }}>
                      {(detectionResult.tier1_score * 100).toFixed(1)}%
                    </div>
                    <div style={{ fontSize: "0.7rem", color: "var(--text-secondary)" }}>{detectionResult.tier1_latency_ms} ms</div>
                  </div>

                  <div style={{ padding: "12px", background: "rgba(255,255,255,0.03)", borderRadius: "8px" }}>
                    <div style={{ fontSize: "0.72rem", color: "var(--text-muted)", fontWeight: 700 }}>TIER 2 (GNN)</div>
                    <div style={{ fontSize: "1.1rem", fontWeight: 800, color: "var(--accent-purple)", margin: "4px 0" }}>
                      {detectionResult.tier2_score !== null ? `${(detectionResult.tier2_score * 100).toFixed(1)}%` : "BYPASSED"}
                    </div>
                    <div style={{ fontSize: "0.7rem", color: "var(--text-secondary)" }}>
                      {detectionResult.tier2_latency_ms ? `${detectionResult.tier2_latency_ms} ms` : "Fast path"}
                    </div>
                  </div>

                  <div style={{ padding: "12px", background: "rgba(255,255,255,0.03)", borderRadius: "8px" }}>
                    <div style={{ fontSize: "0.72rem", color: "var(--text-muted)", fontWeight: 700 }}>TIER 3 (SAR)</div>
                    <div style={{ fontSize: "1.1rem", fontWeight: 800, color: "var(--accent-green)", margin: "4px 0" }}>
                      {detectionResult.sar_report ? "GENERATED" : "INACTIVE"}
                    </div>
                    <div style={{ fontSize: "0.7rem", color: "var(--text-secondary)" }}>Async narrative</div>
                  </div>
                </div>
              </div>

              {/* SAR Narrative View */}
              {detectionResult.sar_report && (
                <div className="glass-card" style={{ padding: "24px" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "14px" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                      <FileText size={18} color="var(--accent-green)" />
                      <h4 style={{ fontSize: "0.95rem", fontWeight: 700 }}>
                        FinCEN Automated SAR Report ({detectionResult.sar_report.sar_id})
                      </h4>
                    </div>
                    <button
                      onClick={() => {
                        navigator.clipboard.writeText(detectionResult.sar_report.narrative_text);
                        setCopied(true);
                        setTimeout(() => setCopied(false), 2000);
                      }}
                      className="btn-secondary"
                      style={{ fontSize: "0.75rem", padding: "4px 10px" }}
                    >
                      <Copy size={12} />
                      {copied ? "Copied!" : "Copy SAR"}
                    </button>
                  </div>

                  <pre
                    style={{
                      background: "#04060c",
                      border: "1px solid var(--border-color)",
                      borderRadius: "8px",
                      padding: "16px",
                      fontSize: "0.8rem",
                      whiteSpace: "pre-wrap",
                      color: "#e2e8f0",
                      lineHeight: "1.5",
                    }}
                  >
                    {detectionResult.sar_report.narrative_text}
                  </pre>
                </div>
              )}
            </>
          ) : (
            <div className="glass-card" style={{ padding: "48px 24px", textAlign: "center", color: "var(--text-muted)" }}>
              <Shield size={48} color="rgba(255,255,255,0.2)" style={{ margin: "0 auto 16px" }} />
              <h4 style={{ fontSize: "1.1rem", fontWeight: 600, color: "var(--text-secondary)", marginBottom: "6px" }}>
                Ready to Evaluate
              </h4>
              <p style={{ fontSize: "0.85rem", maxWidth: "360px", margin: "0 auto" }}>
                Submit a transaction payload on the left to trigger the real-time cascading detection grid and inspect sub-30ms execution.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
