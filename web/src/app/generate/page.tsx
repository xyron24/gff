"use client";

import { useEffect, useState, useRef } from "react";
import { Radio, Play, Pause, RefreshCw, FileCode, CheckCircle, AlertTriangle, ShieldAlert, X } from "lucide-react";
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
    <div className="flex flex-col gap-4 w-full">
      {/* Header Bar */}
      <div className="terminal-panel p-4 flex flex-wrap items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="badge-clean badge-telemetry font-mono">PILLAR 2: GENERATE</span>
            <h1 className="font-bold text-sm text-slate-100 tracking-tight">
              ADVERSARIAL SIMULATION &amp; ISO 20022 PAYLOAD CONTROLLER
            </h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Generate empirical Poisson arrival baseline payment streams and inject 12 GenAI attack vectors with ISO 20022 formatting.
          </p>
        </div>

        <button
          onClick={() => setStreamActive(!streamActive)}
          className="btn-subtle text-xs font-mono"
        >
          {streamActive ? <Pause size={13} /> : <Play size={13} />}
          <span>{streamActive ? "PAUSE LIVE STREAM" : "RESUME LIVE STREAM"}</span>
        </button>
      </div>

      {/* Control Configuration Panel */}
      <div className="terminal-panel p-4 grid grid-cols-1 sm:grid-cols-3 gap-4 items-center text-xs">
        <div>
          <div className="flex justify-between font-mono text-[10px] text-slate-400 mb-1.5 uppercase">
            <span>FRAUD INJECTION RATIO</span>
            <span className="text-[#FF5F00] font-bold">{(fraudRatio * 100).toFixed(0)}%</span>
          </div>
          <input
            type="range"
            min="0.05"
            max="0.50"
            step="0.05"
            value={fraudRatio}
            onChange={(e) => setFraudRatio(parseFloat(e.target.value))}
            className="w-full accent-[#FF5F00]"
          />
        </div>

        <div>
          <div className="font-mono text-[10px] text-slate-400 mb-1.5 uppercase">BATCH INJECTION SIZE</div>
          <select
            value={batchCount}
            onChange={(e) => setBatchCount(parseInt(e.target.value))}
            className="w-full bg-[#131722] border border-[#1C2230] rounded px-3 py-1.5 text-xs font-mono text-slate-200 outline-none focus:border-[#FF5F00]"
          >
            <option value="25">25 Transactions</option>
            <option value="50">50 Transactions</option>
            <option value="100">100 Transactions</option>
            <option value="250">250 Transactions</option>
          </select>
        </div>

        <div className="flex items-end">
          <button
            onClick={handleBatchGenerate}
            disabled={isGenerating}
            className="btn-ember w-full justify-center py-2 text-xs font-mono font-bold uppercase"
          >
            <RefreshCw size={13} className={isGenerating ? "animate-spin" : ""} />
            <span>{isGenerating ? "Injecting Payload..." : "Inject Attack Batch"}</span>
          </button>
        </div>
      </div>

      {/* Live Ledger Table & Drawer */}
      <div className={`grid ${selectedXmlTxn ? "grid-cols-1 lg:grid-cols-12" : "grid-cols-1"} gap-3`}>
        <div className={`${selectedXmlTxn ? "lg:col-span-7" : "w-full"} terminal-panel flex flex-col h-[640px]`}>
          <div className="terminal-header">
            <div className="terminal-title">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              <span>TRANSACTION LEDGER FEED ({streamEvents.length} BUFFERED)</span>
            </div>
            <span className="font-mono text-[10px] text-slate-500">FORMAT: ISO 20022 XML / JSON</span>
          </div>

          <div className="flex-1 overflow-y-auto">
            <table className="terminal-table">
              <thead>
                <tr>
                  <th>TXN ID</th>
                  <th>TIMESTAMP</th>
                  <th>ORIGIN &rarr; DEST</th>
                  <th className="text-right">AMOUNT</th>
                  <th>RAIL</th>
                  <th>DECISION</th>
                  <th>ACTION</th>
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
                      className={isBlock ? "border-l-2 border-l-rose-500 bg-rose-950/15" : "hover:bg-[#131722]"}
                    >
                      <td className="font-mono text-slate-200 font-bold text-xs">{txn.txn_id}</td>
                      <td className="font-mono text-[10px] text-slate-500">
                        {txn.timestamp ? txn.timestamp.slice(11, 19) : "--:--:--"}
                      </td>
                      <td className="font-mono text-[11px]">
                        <span className="text-slate-300">{txn.sender_account}</span>
                        <span className="text-slate-500 mx-1">&rarr;</span>
                        <span className="text-slate-400">{txn.receiver_account}</span>
                      </td>
                      <td className="text-right font-mono font-bold text-slate-100 text-xs">
                        ${Number(txn.amount || 0).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                      </td>
                      <td>
                        <span className="badge-clean badge-neutral text-[9px]">
                          {txn.channel || "ONLINE"}
                        </span>
                      </td>
                      <td>
                        {isBlock ? (
                          <span className="badge-clean badge-threat">BLOCK</span>
                        ) : (
                          <span className="badge-clean badge-approved">APPROVE</span>
                        )}
                      </td>
                      <td>
                        <button
                          onClick={() => setSelectedXmlTxn(evt)}
                          className="text-[10px] font-mono text-sky-400 hover:underline"
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
        </div>

        {/* ISO XML Inspector Drawer */}
        {selectedXmlTxn && (
          <div className="lg:col-span-5 terminal-panel flex flex-col h-[640px] bg-[#0A0D13]">
            <div className="terminal-header">
              <div className="terminal-title text-slate-200">
                <FileCode size={13} className="text-sky-400" />
                <span>ISO 20022 XML PAYLOAD</span>
              </div>
              <button onClick={() => setSelectedXmlTxn(null)} className="text-slate-500 hover:text-slate-200">
                <X size={14} />
              </button>
            </div>

            <div className="p-3 border-b border-[#1C2230] font-mono text-xs text-slate-400">
              MESSAGE TYPE: <span className="text-sky-400 font-bold">{selectedXmlTxn.transaction?.iso_message_type || "pacs.008.001.08"}</span>
            </div>

            <pre className="flex-1 p-3 font-mono text-[10px] text-sky-300 overflow-y-auto leading-relaxed bg-[#08090C]">
              {selectedXmlTxn.iso_xml || "XML Payload Unavailable"}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}
