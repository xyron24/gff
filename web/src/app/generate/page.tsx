"use client";

import { useEffect, useState, useRef } from "react";
import { Radio, Play, Pause, RefreshCw, FileCode, CheckCircle, AlertTriangle, ShieldAlert } from "lucide-react";
import { triggerGenerate, getWebSocketUrl } from "@/lib/api";

export default function GeneratePage() {
  const [streamActive, setStreamActive] = useState(true);
  const [streamEvents, setStreamEvents] = useState<any[]>([]);
  const [fraudRatio, setFraudRatio] = useState(0.15);
  const [batchCount, setBatchCount] = useState(50);
  const [isGenerating, setIsGenerating] = useState(false);
  const [selectedXmlTxn, setSelectedXmlTxn] = useState<any>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!streamActive) {
      if (wsRef.current) wsRef.current.close();
      return;
    }

    const wsUrl = getWebSocketUrl();
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setStreamEvents((prev) => [data, ...prev.slice(0, 49)]);
      } catch (err) {
        console.error("WS error:", err);
      }
    };

    return () => {
      ws.close();
    };
  }, [streamActive]);

  async function handleBatchGenerate() {
    setIsGenerating(true);
    try {
      const res = await triggerGenerate({
        n_transactions: batchCount,
        fraud_ratio: fraudRatio,
      });
      // Prepend generated transactions to feed
      const formatted = res.transactions.map((t: any) => ({
        timestamp: t.timestamp,
        transaction: t,
        detection: {
          decision: t.is_fraud ? "BLOCK" : "APPROVE",
          risk_score: t.is_fraud ? 0.92 : 0.04,
          total_latency_ms: 0.85,
        },
        iso_xml: t.iso_xml_preview,
      }));
      setStreamEvents((prev) => [...formatted, ...prev].slice(0, 60));
    } catch (err) {
      console.error("Batch generate failed:", err);
    } finally {
      setIsGenerating(false);
    }
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "28px" }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <div className="badge badge-purple" style={{ marginBottom: "10px" }}>
            PILLAR 2 • ADVERSARIAL SIMULATION
          </div>
          <h1 style={{ fontSize: "2rem", fontWeight: "800", letterSpacing: "-0.02em", marginBottom: "8px" }}>
            Real-Time Settlement & Attack Injection Stream
          </h1>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.95rem" }}>
            Synthesizing realistic baseline financial flows and adversarial GenAI attack payloads with ISO 20022 formatting.
          </p>
        </div>

        <div style={{ display: "flex", gap: "12px" }}>
          <button
            onClick={() => setStreamActive(!streamActive)}
            className={streamActive ? "btn-secondary" : "btn-primary"}
          >
            {streamActive ? <Pause size={16} /> : <Play size={16} />}
            {streamActive ? "Pause Live Stream" : "Resume Stream"}
          </button>
        </div>
      </div>

      {/* Control Panel Card */}
      <div className="glass-card" style={{ padding: "24px" }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "24px", alignItems: "center" }}>
          <div>
            <label style={{ fontSize: "0.82rem", color: "var(--text-muted)", fontWeight: 600, display: "block", marginBottom: "8px" }}>
              FRAUD INJECTION RATIO: {(fraudRatio * 100).toFixed(0)}%
            </label>
            <input
              type="range"
              min="0.05"
              max="0.50"
              step="0.05"
              value={fraudRatio}
              onChange={(e) => setFraudRatio(parseFloat(e.target.value))}
              style={{ width: "100%", accentColor: "var(--accent-cyan)" }}
            />
          </div>

          <div>
            <label style={{ fontSize: "0.82rem", color: "var(--text-muted)", fontWeight: 600, display: "block", marginBottom: "8px" }}>
              BATCH SIZE: {batchCount} TXNS
            </label>
            <select
              value={batchCount}
              onChange={(e) => setBatchCount(parseInt(e.target.value))}
              style={{
                width: "100%",
                padding: "8px 12px",
                borderRadius: "8px",
                background: "rgba(255, 255, 255, 0.04)",
                border: "1px solid var(--border-color)",
                color: "var(--text-primary)",
                outline: "none",
              }}
            >
              <option value="25">25 Transactions</option>
              <option value="50">50 Transactions</option>
              <option value="100">100 Transactions</option>
              <option value="250">250 Transactions</option>
            </select>
          </div>

          <div style={{ display: "flex", alignItems: "flex-end", height: "100%" }}>
            <button
              onClick={handleBatchGenerate}
              disabled={isGenerating}
              className="btn-primary"
              style={{ width: "100%", justifyContent: "center" }}
            >
              <RefreshCw size={16} className={isGenerating ? "animate-spin" : ""} />
              {isGenerating ? "Generating..." : "Inject Attack Batch"}
            </button>
          </div>
        </div>
      </div>

      {/* Main Stream Table */}
      <div style={{ display: "grid", gridTemplateColumns: selectedXmlTxn ? "1.3fr 1fr" : "1fr", gap: "24px" }}>
        <div className="glass-card" style={{ padding: "20px", overflowX: "auto" }}>
          <h3 style={{ fontSize: "1.1rem", fontWeight: 700, marginBottom: "16px", display: "flex", alignItems: "center", gap: "8px" }}>
            <span className="status-dot" />
            Live Settlement Ledger Stream ({streamEvents.length} transactions buffered)
          </h3>

          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.85rem" }}>
            <thead>
              <tr style={{ borderBottom: "1px solid var(--border-color)", color: "var(--text-muted)", textAlign: "left" }}>
                <th style={{ padding: "10px" }}>TXN ID</th>
                <th style={{ padding: "10px" }}>TIMESTAMP</th>
                <th style={{ padding: "10px" }}>ORIGINATOR &rarr; BENEFICIARY</th>
                <th style={{ padding: "10px" }}>AMOUNT</th>
                <th style={{ padding: "10px" }}>RAIL</th>
                <th style={{ padding: "10px" }}>DECISION</th>
                <th style={{ padding: "10px" }}>ACTION</th>
              </tr>
            </thead>
            <tbody>
              {streamEvents.map((evt, idx) => {
                const txn = evt.transaction || {};
                const det = evt.detection || {};
                const isBlock = det.decision === "BLOCK" || txn.is_fraud === 1;

                return (
                  <tr
                    key={txn.txn_id || idx}
                    style={{
                      borderBottom: "1px solid rgba(255,255,255,0.04)",
                      background: isBlock ? "rgba(239, 68, 68, 0.05)" : "transparent",
                    }}
                  >
                    <td style={{ padding: "12px 10px", fontFamily: "var(--font-mono)", fontWeight: 700, color: isBlock ? "var(--accent-red)" : "var(--text-primary)" }}>
                      {txn.txn_id}
                    </td>
                    <td style={{ padding: "12px 10px", color: "var(--text-muted)", fontSize: "0.78rem" }}>
                      {txn.timestamp ? txn.timestamp.slice(11, 19) : "--:--:--"}
                    </td>
                    <td style={{ padding: "12px 10px" }}>
                      <div style={{ fontWeight: 600 }}>{txn.sender_account}</div>
                      <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>&rarr; {txn.receiver_account}</div>
                    </td>
                    <td style={{ padding: "12px 10px", fontWeight: 700 }}>
                      ${Number(txn.amount || 0).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                    </td>
                    <td style={{ padding: "12px 10px" }}>
                      <span className="badge badge-purple" style={{ fontSize: "0.68rem" }}>
                        {txn.channel || "ONLINE"}
                      </span>
                    </td>
                    <td style={{ padding: "12px 10px" }}>
                      {isBlock ? (
                        <span className="badge badge-red" style={{ fontSize: "0.7rem" }}>
                          BLOCK ({((det.risk_score || 0.95) * 100).toFixed(0)}%)
                        </span>
                      ) : (
                        <span className="badge badge-green" style={{ fontSize: "0.7rem" }}>
                          APPROVE ({det.total_latency_ms || 0.8}ms)
                        </span>
                      )}
                    </td>
                    <td style={{ padding: "12px 10px" }}>
                      <button
                        onClick={() => setSelectedXmlTxn(evt)}
                        style={{
                          background: "rgba(0, 212, 255, 0.1)",
                          border: "1px solid rgba(0, 212, 255, 0.3)",
                          color: "var(--accent-cyan)",
                          padding: "4px 8px",
                          borderRadius: "4px",
                          fontSize: "0.75rem",
                          cursor: "pointer",
                        }}
                      >
                        ISO XML
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* ISO XML Drawer */}
        {selectedXmlTxn && (
          <div className="glass-card" style={{ padding: "24px", display: "flex", flexDirection: "column", gap: "14px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <h3 style={{ fontSize: "1rem", fontWeight: 700, display: "flex", alignItems: "center", gap: "8px" }}>
                <FileCode size={18} color="var(--accent-cyan)" />
                ISO 20022 XML Message Inspector
              </h3>
              <button
                onClick={() => setSelectedXmlTxn(null)}
                style={{ background: "transparent", border: "none", color: "var(--text-muted)", cursor: "pointer" }}
              >
                &times;
              </button>
            </div>

            <div style={{ fontSize: "0.82rem", color: "var(--text-secondary)" }}>
              Message Type: <span style={{ color: "var(--accent-cyan)", fontWeight: 700 }}>{selectedXmlTxn.transaction?.iso_message_type || "pacs.008.001.08"}</span>
            </div>

            <pre
              style={{
                background: "#04060c",
                border: "1px solid var(--border-color)",
                borderRadius: "8px",
                padding: "16px",
                fontSize: "0.75rem",
                overflowX: "auto",
                maxHeight: "500px",
                color: "#7dd3fc",
                lineHeight: "1.4",
              }}
            >
              {selectedXmlTxn.iso_xml || "XML Payload Unavailable"}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}
