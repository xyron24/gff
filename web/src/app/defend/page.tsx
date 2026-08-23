"use client";

import { useState } from "react";
import { Shield, Zap, FileText, CheckCircle2, AlertTriangle, ShieldAlert, ArrowRight, Copy } from "lucide-react";
import { scoreTransaction } from "@/lib/api";
import SarMarkdownViewer from "@/components/SarMarkdownViewer";

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
    <div className="flex flex-col gap-4 w-full">
      {/* Header Bar */}
      <div className="terminal-panel p-4 flex flex-wrap items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="badge-clean badge-approved font-mono">PILLAR 3: DEFEND</span>
            <h1 className="font-bold text-sm text-slate-100 tracking-tight">
              CASCADING MULTI-TIER DETECTION GRID &amp; COGNITIVE SAR ENGINE
            </h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Real-time payment authorization: Tier 1 GBDT (&lt;1ms) $\to$ Tier 2 DyGNN relational analysis $\to$ Tier 3 Cognitive SAR generation.
          </p>
        </div>

        {/* Presets */}
        <div className="flex items-center gap-1.5 font-mono text-xs">
          <span className="text-slate-500">LOAD PRESET:</span>
          <button onClick={() => handlePreset("smurf")} className="btn-subtle py-1 px-2.5 text-xs">
            ATK-001 Smurf
          </button>
          <button onClick={() => handlePreset("ato")} className="btn-subtle py-1 px-2.5 text-xs">
            ATK-012 ATO
          </button>
          <button onClick={() => handlePreset("legit")} className="btn-subtle py-1 px-2.5 text-xs">
            Clean Retail
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Form Panel */}
        <div className="lg:col-span-5 terminal-panel p-4 flex flex-col gap-3">
          <div className="terminal-title text-slate-200">
            <span>SWITCH AUTHORIZATION SIMULATOR</span>
          </div>

          <div className="grid grid-cols-2 gap-3 text-xs">
            <div>
              <label className="text-[10px] font-mono text-slate-500 block mb-1 uppercase">TRANSACTION AMOUNT ($)</label>
              <input
                type="number"
                value={amount}
                onChange={(e) => setAmount(parseFloat(e.target.value) || 0)}
                className="w-full bg-[#131722] border border-[#1C2230] rounded px-3 py-1.5 text-xs font-mono text-slate-100 outline-none focus:border-[#FF5F00]"
              />
            </div>

            <div>
              <label className="text-[10px] font-mono text-slate-500 block mb-1 uppercase">PAYMENT CHANNEL</label>
              <select
                value={channel}
                onChange={(e) => setChannel(e.target.value)}
                className="w-full bg-[#131722] border border-[#1C2230] rounded px-3 py-1.5 text-xs font-mono text-slate-100 outline-none"
              >
                <option value="ONLINE">ONLINE (Card-Not-Present)</option>
                <option value="POS">POS (Point of Sale)</option>
                <option value="WIRE">WIRE / SWIFT RTGS</option>
                <option value="API">Open Banking API (PISP)</option>
              </select>
            </div>

            <div>
              <label className="text-[10px] font-mono text-slate-500 block mb-1 uppercase">ORIGIN ACCOUNT</label>
              <input
                type="text"
                value={sender}
                onChange={(e) => setSender(e.target.value)}
                className="w-full bg-[#131722] border border-[#1C2230] rounded px-3 py-1.5 text-xs font-mono text-slate-100 outline-none"
              />
            </div>

            <div>
              <label className="text-[10px] font-mono text-slate-500 block mb-1 uppercase">BENEFICIARY ACCOUNT</label>
              <input
                type="text"
                value={receiver}
                onChange={(e) => setReceiver(e.target.value)}
                className="w-full bg-[#131722] border border-[#1C2230] rounded px-3 py-1.5 text-xs font-mono text-slate-100 outline-none"
              />
            </div>

            <div>
              <label className="text-[10px] font-mono text-slate-500 block mb-1 uppercase">SESSION DURATION ({sessionDuration}s)</label>
              <input
                type="number"
                step="0.5"
                value={sessionDuration}
                onChange={(e) => setSessionDuration(parseFloat(e.target.value) || 0)}
                className="w-full bg-[#131722] border border-[#1C2230] rounded px-3 py-1.5 text-xs font-mono text-slate-100 outline-none"
              />
            </div>

            <div>
              <label className="text-[10px] font-mono text-slate-500 block mb-1 uppercase">BIOMETRIC FRICTION ({frictionScore})</label>
              <input
                type="number"
                step="0.01"
                min="0"
                max="1"
                value={frictionScore}
                onChange={(e) => setFrictionScore(parseFloat(e.target.value) || 0)}
                className="w-full bg-[#131722] border border-[#1C2230] rounded px-3 py-1.5 text-xs font-mono text-slate-100 outline-none"
              />
            </div>
          </div>

          <div>
            <label className="text-[10px] font-mono text-slate-500 block mb-1 uppercase">ISO 20022 REMITTANCE TEXT</label>
            <input
              type="text"
              value={remittanceText}
              onChange={(e) => setRemittanceText(e.target.value)}
              className="w-full bg-[#131722] border border-[#1C2230] rounded px-3 py-1.5 text-xs font-mono text-slate-100 outline-none"
            />
          </div>

          <button
            onClick={handleScore}
            disabled={loading}
            className="btn-ember w-full justify-center py-2 text-xs font-mono font-bold tracking-wider uppercase mt-1"
          >
            <Zap size={14} />
            <span>{loading ? "SCREENING CASCADE..." : "EXECUTE REAL-TIME AUTHORIZATION SCREENING"}</span>
          </button>
        </div>

        {/* Results & Latency Trace */}
        <div className="lg:col-span-7 flex flex-col gap-3">
          {detectionResult ? (
            <div className="terminal-panel p-4 flex flex-col gap-3">
              {/* Decision Badge */}
              <div
                className={`p-3 rounded border flex items-center justify-between ${
                  detectionResult.decision === "BLOCK"
                    ? "bg-rose-950/20 border-rose-800/40 text-rose-300"
                    : "bg-emerald-950/20 border-emerald-800/40 text-emerald-300"
                }`}
              >
                <div className="flex items-center gap-2">
                  {detectionResult.decision === "BLOCK" ? (
                    <ShieldAlert size={20} className="text-rose-400" />
                  ) : (
                    <CheckCircle2 size={20} className="text-emerald-400" />
                  )}
                  <div>
                    <div className="font-mono text-sm font-bold">DECISION: {detectionResult.decision}</div>
                    <div className="text-[11px] text-slate-400 font-mono">
                      COMPOSITE RISK SCORE: {(detectionResult.risk_score * 100).toFixed(1)}%
                    </div>
                  </div>
                </div>

                <div className="font-mono text-xs font-bold text-sky-400">
                  TOTAL LATENCY: {detectionResult.total_latency_ms.toFixed(2)} ms
                </div>
              </div>

              {/* Segmented Micro-Progress Waterfall */}
              <div className="bg-[#08090C] border border-[#1C2230] rounded p-3 flex flex-col gap-2">
                <div className="flex items-center justify-between font-mono text-[10px]">
                  <span className="text-slate-400 uppercase font-semibold">Cascade Latency Waterfall</span>
                  <span className="text-sky-400 font-bold">{detectionResult.total_latency_ms.toFixed(2)}ms / 30.00ms SLA</span>
                </div>

                <div className="w-full bg-[#131722] h-3 rounded overflow-hidden flex border border-[#1C2230]">
                  <div
                    style={{ width: `${Math.min(100, (detectionResult.tier1_latency_ms / 30) * 100)}%` }}
                    className="bg-sky-500 h-full"
                    title={`Tier 1 (GBDT): ${detectionResult.tier1_latency_ms.toFixed(2)}ms`}
                  />
                  {detectionResult.tier2_latency_ms ? (
                    <div
                      style={{ width: `${Math.min(100, (detectionResult.tier2_latency_ms / 30) * 100)}%` }}
                      className="bg-purple-500 h-full"
                      title={`Tier 2 (GNN): ${detectionResult.tier2_latency_ms.toFixed(2)}ms`}
                    />
                  ) : null}
                </div>

                <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 pt-1 border-t border-[#141822]">
                  <div>
                    <span className="text-sky-400 font-bold">T1 (GBDT):</span> {detectionResult.tier1_latency_ms.toFixed(2)}ms
                  </div>
                  <div>
                    <span className="text-purple-400 font-bold">T2 (GNN):</span>{" "}
                    {detectionResult.tier2_latency_ms ? `${detectionResult.tier2_latency_ms.toFixed(2)}ms` : "Bypassed"}
                  </div>
                </div>
              </div>

              {/* Formatted Markdown SAR Viewer */}
              {detectionResult.sar_report && (
                <SarMarkdownViewer sarReport={detectionResult.sar_report} />
              )}
            </div>
          ) : (
            <div className="terminal-panel p-12 flex flex-col items-center justify-center text-center text-slate-500 text-xs">
              <Shield size={36} className="opacity-30 mb-2 text-slate-400" />
              <span className="font-mono text-sm text-slate-300">Ready for Switch Authorization</span>
              <span className="text-xs text-slate-500 max-w-sm mt-1">
                Configure transaction parameters and execute screening to inspect cascading decisions and automated regulatory narratives.
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
