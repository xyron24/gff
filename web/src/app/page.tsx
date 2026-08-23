"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import * as d3 from "d3";
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  ChevronRight,
  Clock,
  Cpu,
  FileCode,
  FileText,
  Network,
  Pause,
  Play,
  Radio,
  RefreshCw,
  Search,
  Shield,
  ShieldAlert,
  X,
  Zap,
} from "lucide-react";
import { fetchGraph, fetchHealth, fetchMetrics, getWebSocketUrl, scoreTransaction } from "@/lib/api";
import TelemetryRibbon from "@/components/TelemetryRibbon";
import SarMarkdownViewer from "@/components/SarMarkdownViewer";

export default function CommandCenter() {
  // Telemetry KPIs
  const [metrics, setMetrics] = useState<any>({
    tier1_latency_p99_ms: 0.85,
    cascading_latency_p99_ms: 18.4,
    overall_precision: 0.942,
    overall_recall: 0.915,
    f1_score: 0.928,
    pr_auc: 0.967,
    false_positive_rate: 0.018,
    throughput_tps: 1420,
  });

  // Stream State
  const [streamActive, setStreamActive] = useState<boolean>(true);
  const [streamEvents, setStreamEvents] = useState<any[]>([]);
  const [streamFilter, setStreamFilter] = useState<string>("ALL");
  const [selectedTxn, setSelectedTxn] = useState<any>(null);

  // Graph State
  const svgRef = useRef<SVGSVGElement | null>(null);
  const [graphData, setGraphData] = useState<any>(null);
  const [graphFilter, setGraphFilter] = useState<string>("ALL");
  const [selectedNode, setSelectedNode] = useState<any>(null);

  // Detection Testing Console State
  const [testAmount, setTestAmount] = useState<number>(495.0);
  const [testChannel, setTestChannel] = useState<string>("ONLINE");
  const [testSender, setTestSender] = useState<string>("ACC-000420");
  const [testReceiver, setTestReceiver] = useState<string>("MERCH-00088");
  const [testFriction, setTestFriction] = useState<number>(0.02);
  const [testDuration, setTestDuration] = useState<number>(3.5);
  const [evaluating, setEvaluating] = useState<boolean>(false);
  const [detectionResult, setDetectionResult] = useState<any>(null);

  // Initial Load
  useEffect(() => {
    async function init() {
      try {
        const [m, g] = await Promise.all([fetchMetrics(), fetchGraph(90)]);
        if (m?.kpis) setMetrics(m.kpis);
        if (g) setGraphData(g);
      } catch (err) {
        console.error("Init load error:", err);
      }
    }
    init();
  }, []);

  // WebSocket Live Transaction Streamer
  useEffect(() => {
    if (!streamActive) return;

    const wsUrl = getWebSocketUrl();
    let ws: WebSocket;
    try {
      ws = new WebSocket(wsUrl);
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setStreamEvents((prev) => [data, ...prev.slice(0, 49)]);
        } catch (err) {
          console.error("Stream parse error:", err);
        }
      };
    } catch (e) {
      console.warn("WebSocket not reachable, operating offline");
    }

    return () => {
      if (ws) ws.close();
    };
  }, [streamActive]);

  // Spacebar hotkey to pause/resume
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if (e.code === "Space" && e.target === document.body) {
        e.preventDefault();
        setStreamActive((prev) => !prev);
      }
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  // D3 Force-Directed Graph Rendering with Radar Coordinates
  useEffect(() => {
    if (!graphData || !svgRef.current) return;

    const width = svgRef.current.clientWidth || 500;
    const height = svgRef.current.clientHeight || 450;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    // 1. SVG Defs for Glowing Mule Filter & Gradient
    const defs = svg.append("defs");
    
    // Radial Background Rings & Crosshairs
    const gridGroup = svg.append("g").attr("class", "radar-grid");
    const cx = width / 2;
    const cy = height / 2;
    const maxRadius = Math.min(width, height) * 0.45;

    // Concentric polar coordinate rings
    [0.25, 0.5, 0.75, 1.0].forEach((ratio) => {
      gridGroup
        .append("circle")
        .attr("cx", cx)
        .attr("cy", cy)
        .attr("r", maxRadius * ratio)
        .attr("fill", "none")
        .attr("stroke", "#1A1F2C")
        .attr("stroke-width", 1)
        .attr("stroke-dasharray", "3 3");
    });

    // Crosshair axes
    gridGroup
      .append("line")
      .attr("x1", cx)
      .attr("y1", cy - maxRadius)
      .attr("x2", cx)
      .attr("y2", cy + maxRadius)
      .attr("stroke", "#1A1F2C")
      .attr("stroke-width", 1);

    gridGroup
      .append("line")
      .attr("x1", cx - maxRadius)
      .attr("y1", cy)
      .attr("x2", cx + maxRadius)
      .attr("y2", cy)
      .attr("stroke", "#1A1F2C")
      .attr("stroke-width", 1);

    // Main Graph Container
    const g = svg.append("g");

    // Zoom behavior
    const zoom = d3.zoom().scaleExtent([0.4, 3.5]).on("zoom", (event) => {
      g.attr("transform", event.transform);
    });
    svg.call(zoom as any);

    // Filter nodes
    let filteredNodes = graphData.nodes.map((d: any) => ({ ...d }));
    if (graphFilter === "MULES") {
      filteredNodes = filteredNodes.filter((d: any) => d.is_fraud);
    } else if (graphFilter === "MERCHANTS") {
      filteredNodes = filteredNodes.filter((d: any) => d.type === "merchant");
    } else if (graphFilter === "DEVICES") {
      filteredNodes = filteredNodes.filter((d: any) => d.type === "device" || d.type === "ip");
    }

    const nodeIds = new Set(filteredNodes.map((n: any) => n.id));
    const filteredLinks = graphData.links
      .filter((l: any) => nodeIds.has(l.source?.id || l.source) && nodeIds.has(l.target?.id || l.target))
      .map((l: any) => ({ ...l }));

    const simulation = d3
      .forceSimulation(filteredNodes)
      .force("link", d3.forceLink(filteredLinks).id((d: any) => d.id).distance(50))
      .force("charge", d3.forceManyBody().strength(-110))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide().radius((d: any) => (d.is_fraud ? 18 : 12)));

    // Links (Normal: slate lines #334155, Flagged Mule: dashed crimson #EF4444)
    const link = g
      .append("g")
      .selectAll("line")
      .data(filteredLinks)
      .enter()
      .append("line")
      .attr("stroke", (d: any) => (d.is_fraud ? "#EF4444" : "#334155"))
      .attr("stroke-width", (d: any) => (d.is_fraud ? 1.8 : 0.8))
      .attr("stroke-dasharray", (d: any) => (d.is_fraud ? "4,3" : "none"))
      .attr("opacity", (d: any) => (d.is_fraud ? 0.95 : 0.45));

    // Node Coloring & Scaled Radii
    const getNodeRadius = (d: any) => {
      if (d.is_fraud) return 10; // Flagged Mule
      if (d.type === "merchant") return 8;
      if (d.type === "device" || d.type === "ip") return 7;
      return 6; // Standard Account
    };

    const getNodeColor = (d: any) => {
      if (d.is_fraud) return "#EF4444";
      if (d.type === "merchant") return "#10B981";
      if (d.type === "device") return "#8B5CF6";
      if (d.type === "ip") return "#F59E0B";
      return "#38BDF8"; // Account
    };

    // Render Nodes
    const nodeGroup = g
      .append("g")
      .selectAll("g")
      .data(filteredNodes)
      .enter()
      .append("g")
      .style("cursor", "pointer")
      .on("click", (event, d) => {
        setSelectedNode(d);
      });

    // Outer pulse ring for flagged nodes
    nodeGroup
      .filter((d: any) => d.is_fraud)
      .append("circle")
      .attr("r", 15)
      .attr("fill", "rgba(239, 68, 68, 0.15)")
      .attr("stroke", "rgba(239, 68, 68, 0.4)")
      .attr("stroke-width", 1)
      .attr("class", "animate-pulse");

    nodeGroup
      .append("circle")
      .attr("r", getNodeRadius)
      .attr("fill", getNodeColor)
      .attr("stroke", "#08090C")
      .attr("stroke-width", 1.5);

    // Node Drag Behavior
    nodeGroup.call(
      d3
        .drag()
        .on("start", (event: any, d: any) => {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
        })
        .on("drag", (event: any, d: any) => {
          d.fx = event.x;
          d.fy = event.y;
        })
        .on("end", (event: any, d: any) => {
          if (!event.active) simulation.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        }) as any
    );

    simulation.on("tick", () => {
      link
        .attr("x1", (d: any) => d.source.x)
        .attr("y1", (d: any) => d.source.y)
        .attr("x2", (d: any) => d.target.x)
        .attr("y2", (d: any) => d.target.y);

      nodeGroup.attr("transform", (d: any) => `translate(${d.x},${d.y})`);
    });

    return () => {
      simulation.stop();
    };
  }, [graphData, graphFilter]);

  // Execute single transaction test
  async function handleExecuteScreening() {
    setEvaluating(true);
    try {
      const payload = {
        transaction: {
          txn_id: `TXN-MANUAL-${Math.floor(Math.random() * 900000 + 100000)}`,
          timestamp: new Date().toISOString(),
          sender_account: testSender,
          receiver_account: testReceiver,
          amount: testAmount,
          channel: testChannel,
          mcc: "4829",
          session_duration_sec: testDuration,
          biometric_friction_score: testFriction,
          remittance_info: `P2P Transfer to ${testReceiver}`,
          is_foreign_transaction: testChannel === "WIRE",
        },
        generate_sar: true,
      };

      const res = await scoreTransaction(payload);
      setDetectionResult(res);
    } catch (err) {
      console.error("Screening error:", err);
    } finally {
      setEvaluating(false);
    }
  }

  function handleQuickLoad(preset: string) {
    if (preset === "smurf") {
      setTestAmount(195.50);
      setTestChannel("ONLINE");
      setTestSender("ACC-SMURF-09");
      setTestReceiver("ACC-MULE-88");
      setTestFriction(0.14);
      setTestDuration(18.0);
    } else if (preset === "ato") {
      setTestAmount(18500.00);
      setTestChannel("API");
      setTestSender("ACC-VIP-002");
      setTestReceiver("ACC-OFFSHORE");
      setTestFriction(0.012);
      setTestDuration(2.8);
    } else {
      setTestAmount(42.50);
      setTestChannel("POS");
      setTestSender("ACC-000102");
      setTestReceiver("MERCH-GROCERY-01");
      setTestFriction(0.04);
      setTestDuration(45.0);
    }
  }

  const filteredStream = streamEvents.filter((evt) => {
    if (streamFilter === "ALL") return true;
    if (streamFilter === "BLOCK") return evt.detection?.decision === "BLOCK" || evt.transaction?.is_fraud === 1;
    if (streamFilter === "APPROVE") return evt.detection?.decision === "APPROVE";
    return true;
  });

  return (
    <div className="flex flex-col gap-2.5 w-full">
      {/* 1. TOP TELEMETRY RIBBON */}
      <TelemetryRibbon metrics={metrics} />

      {/* 2. DENSE 3-COLUMN WORKSPACE */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-2.5 w-full">
        {/* ========================================================================= */}
        {/* COLUMN 1: LIVE SETTLEMENT STREAM (4 Cols) */}
        {/* ========================================================================= */}
        <div className="xl:col-span-4 terminal-panel flex flex-col h-[700px]">
          {/* Header */}
          <div className="terminal-header">
            <div className="terminal-title">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              <span>LIVE SETTLEMENT STREAM</span>
              <span className="text-slate-500 font-mono text-[10px]">({streamEvents.length})</span>
            </div>

            <div className="flex items-center gap-1.5">
              <button
                onClick={() => setStreamActive(!streamActive)}
                className="btn-subtle text-[10px] py-0.5 px-2 font-mono"
                title="Toggle Stream (Space)"
              >
                {streamActive ? <Pause size={11} /> : <Play size={11} />}
                <span>{streamActive ? "PAUSE" : "RESUME"}</span>
              </button>

              <div className="flex items-center bg-[#08090C] rounded border border-[#1C2230] p-0.5 text-[9px] font-mono">
                {["ALL", "BLOCK", "APPROVE"].map((f) => (
                  <button
                    key={f}
                    onClick={() => setStreamFilter(f)}
                    className={`px-1.5 py-0.5 rounded ${
                      streamFilter === f ? "bg-[#1C2230] text-slate-100 font-bold" : "text-slate-500"
                    }`}
                  >
                    {f}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Monospace Dense Table with Left-Border Threat Highlights */}
          <div className="flex-1 overflow-y-auto">
            <table className="terminal-table">
              <thead>
                <tr>
                  <th>TXN ID</th>
                  <th>ORIGIN &rarr; DEST</th>
                  <th className="text-right">AMOUNT</th>
                  <th>RAIL</th>
                  <th>STATUS</th>
                  <th>LAT</th>
                </tr>
              </thead>
              <tbody>
                {filteredStream.map((evt, idx) => {
                  const txn = evt.transaction || {};
                  const det = evt.detection || {};
                  const isBlock = det.decision === "BLOCK" || txn.is_fraud === 1;

                  return (
                    <tr
                      key={txn.txn_id || idx}
                      onClick={() => setSelectedTxn(evt)}
                      className={`cursor-pointer transition-colors ${
                        selectedTxn?.transaction?.txn_id === txn.txn_id ? "bg-[#131722]" : ""
                      } ${isBlock ? "border-l-2 border-l-rose-500 bg-rose-950/15" : "hover:bg-[#131722]"}`}
                    >
                      <td className="font-mono text-slate-200 font-medium whitespace-nowrap text-[11px]">
                        {txn.txn_id ? txn.txn_id.slice(0, 12) : "TXN-RAW"}
                      </td>
                      <td className="text-[10px] whitespace-nowrap">
                        <div className="text-slate-300 font-mono">{txn.sender_account || "ACC-001"}</div>
                        <div className="text-slate-500 font-mono">&rarr; {txn.receiver_account || "MERCH-01"}</div>
                      </td>
                      <td className="text-right font-mono font-bold whitespace-nowrap text-slate-100 text-xs">
                        ${Number(txn.amount || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                      </td>
                      <td>
                        <span className="badge-clean badge-neutral text-[9px]">
                          {txn.channel || "ONLINE"}
                        </span>
                      </td>
                      <td>
                        {isBlock ? (
                          <span className="badge-clean badge-threat">
                            BLOCK
                          </span>
                        ) : (
                          <span className="badge-clean badge-approved">
                            APPR
                          </span>
                        )}
                      </td>
                      <td className="font-mono text-[10px] text-slate-500 whitespace-nowrap">
                        {det.total_latency_ms ? `${det.total_latency_ms.toFixed(1)}ms` : "<1ms"}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Selected Transaction Inspector Drawer */}
          {selectedTxn && (
            <div className="border-t border-[#1C2230] bg-[#0A0D13] p-2.5 text-xs flex flex-col gap-1.5">
              <div className="flex items-center justify-between font-mono text-[10px]">
                <span className="text-slate-300 font-bold">INSPECT: {selectedTxn.transaction?.txn_id}</span>
                <button onClick={() => setSelectedTxn(null)} className="text-slate-500 hover:text-slate-200">
                  <X size={12} />
                </button>
              </div>
              <div className="bg-[#08090C] border border-[#1C2230] rounded p-2 font-mono text-[9px] text-sky-300 max-h-24 overflow-y-auto leading-relaxed">
                {selectedTxn.iso_xml || JSON.stringify(selectedTxn.transaction, null, 2)}
              </div>
            </div>
          )}
        </div>

        {/* ========================================================================= */}
        {/* COLUMN 2: REAL-TIME MULE GRAPH CANVAS (4 Cols) */}
        {/* ========================================================================= */}
        <div className="xl:col-span-4 terminal-panel flex flex-col h-[700px]">
          {/* Header */}
          <div className="terminal-header">
            <div className="terminal-title">
              <Network size={13} className="text-purple-400" />
              <span>TOPOLOGY &amp; MULE CYCLE GRAPH</span>
            </div>

            <div className="flex items-center gap-1 text-[9px] font-mono">
              {[
                { label: "ALL", val: "ALL" },
                { label: "MULES (RED)", val: "MULES" },
                { label: "MERCHANTS", val: "MERCHANTS" },
              ].map((f) => (
                <button
                  key={f.val}
                  onClick={() => setGraphFilter(f.val)}
                  className={`px-1.5 py-0.5 rounded border ${
                    graphFilter === f.val
                      ? "bg-[#1C2230] text-slate-100 border-[#2D3748] font-bold"
                      : "bg-[#08090C] text-slate-500 border-[#1C2230]"
                  }`}
                >
                  {f.label}
                </button>
              ))}
            </div>
          </div>

          {/* Graph Canvas with Concentric Radar Grid */}
          <div className="flex-1 relative bg-[#08090C] overflow-hidden">
            <svg ref={svgRef} className="w-full h-full" />

            {/* Floating Top-Left Telemetry Overlay */}
            <div className="absolute top-2 left-2 bg-[#0D1017]/90 backdrop-blur border border-[#1C2230] rounded px-2.5 py-1 text-[10px] font-mono text-slate-300 shadow-md">
              <span>Active Graph: </span>
              <span className="text-slate-100 font-bold">{graphData?.total_nodes || 989} Nodes</span>
              <span className="text-slate-500 mx-1">|</span>
              <span className="text-slate-100 font-bold">{graphData?.total_edges || 1200} Edges</span>
              <span className="text-slate-500 mx-1">|</span>
              <span className="text-rose-400 font-bold">4 Cyclic Clusters</span>
            </div>

            {/* Bottom Legend */}
            <div className="absolute bottom-2 left-2 bg-[#0D1017]/90 backdrop-blur border border-[#1C2230] rounded px-2.5 py-1 flex items-center gap-3 text-[9px] font-mono text-slate-400">
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-[#38BDF8]" /> ACC (6px)
              </span>
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-[#10B981]" /> MERCH (8px)
              </span>
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-[#EF4444]" /> MULE / CYCLE (10px)
              </span>
            </div>

            {/* Floating Node Telemetry HUD */}
            {selectedNode && (
              <div className="absolute top-2 right-2 w-56 bg-[#0D1017]/95 backdrop-blur border border-[#2D3748] rounded p-2.5 text-xs flex flex-col gap-1.5 shadow-xl">
                <div className="flex items-center justify-between border-b border-[#1C2230] pb-1">
                  <span className="font-mono font-bold text-[10px] text-slate-100">{selectedNode.id}</span>
                  <button onClick={() => setSelectedNode(null)} className="text-slate-500 hover:text-slate-200">
                    <X size={11} />
                  </button>
                </div>
                <div className="font-mono text-[10px] flex flex-col gap-1">
                  <div className="flex justify-between">
                    <span className="text-slate-500">TYPE:</span>
                    <span className="text-slate-200 uppercase font-semibold">{selectedNode.type}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">MULE RISK:</span>
                    <span className={selectedNode.is_fraud ? "text-rose-400 font-bold" : "text-emerald-400 font-bold"}>
                      {selectedNode.is_fraud ? "FLAGGED CYCLE" : "CLEAN NODE"}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* ========================================================================= */}
        {/* COLUMN 3: CASCADING GRID & SAR TERMINAL (4 Cols) */}
        {/* ========================================================================= */}
        <div className="xl:col-span-4 terminal-panel flex flex-col h-[700px]">
          {/* Header */}
          <div className="terminal-header">
            <div className="terminal-title">
              <Cpu size={13} className="text-[#FF5F00]" />
              <span>CASCADING SUB-30MS GRID &amp; SAR</span>
            </div>
            <span className="badge-clean badge-telemetry text-[9px]">HIST-GBDT + DyGNN</span>
          </div>

          <div className="flex-1 p-3 flex flex-col gap-3 overflow-y-auto">
            {/* Quick Load Presets */}
            <div className="flex items-center gap-1.5">
              <span className="text-[10px] font-mono text-slate-500">PRESETS:</span>
              <button
                onClick={() => handleQuickLoad("smurf")}
                className="btn-subtle text-[10px] py-0.5 px-2 font-mono"
              >
                ATK-001 Smurf
              </button>
              <button
                onClick={() => handleQuickLoad("ato")}
                className="btn-subtle text-[10px] py-0.5 px-2 font-mono"
              >
                ATK-012 ATO
              </button>
              <button
                onClick={() => handleQuickLoad("legit")}
                className="btn-subtle text-[10px] py-0.5 px-2 font-mono"
              >
                Clean Retail
              </button>
            </div>

            {/* Input Form */}
            <div className="bg-[#08090C] border border-[#1C2230] rounded p-2.5 grid grid-cols-2 gap-2 text-xs">
              <div>
                <label className="text-[9px] font-mono text-slate-500 block mb-0.5">AMOUNT ($)</label>
                <input
                  type="number"
                  value={testAmount}
                  onChange={(e) => setTestAmount(parseFloat(e.target.value) || 0)}
                  className="w-full bg-[#131722] border border-[#1C2230] rounded px-2 py-1 text-xs font-mono text-slate-100 outline-none focus:border-[#FF5F00]"
                />
              </div>

              <div>
                <label className="text-[9px] font-mono text-slate-500 block mb-0.5">PAYMENT RAIL</label>
                <select
                  value={testChannel}
                  onChange={(e) => setTestChannel(e.target.value)}
                  className="w-full bg-[#131722] border border-[#1C2230] rounded px-2 py-1 text-xs font-mono text-slate-100 outline-none"
                >
                  <option value="ONLINE">ONLINE (CNP)</option>
                  <option value="POS">POS (Retail)</option>
                  <option value="WIRE">WIRE / SWIFT</option>
                  <option value="API">Open Banking API</option>
                </select>
              </div>

              <div>
                <label className="text-[9px] font-mono text-slate-500 block mb-0.5">ORIGIN ACCOUNT</label>
                <input
                  type="text"
                  value={testSender}
                  onChange={(e) => setTestSender(e.target.value)}
                  className="w-full bg-[#131722] border border-[#1C2230] rounded px-2 py-1 text-[11px] font-mono text-slate-100 outline-none"
                />
              </div>

              <div>
                <label className="text-[9px] font-mono text-slate-500 block mb-0.5">BENEFICIARY</label>
                <input
                  type="text"
                  value={testReceiver}
                  onChange={(e) => setTestReceiver(e.target.value)}
                  className="w-full bg-[#131722] border border-[#1C2230] rounded px-2 py-1 text-[11px] font-mono text-slate-100 outline-none"
                />
              </div>
            </div>

            {/* Action Button */}
            <button
              onClick={handleExecuteScreening}
              disabled={evaluating}
              className="btn-ember w-full justify-center py-2 text-xs font-mono tracking-wider font-bold"
            >
              <Zap size={14} />
              <span>{evaluating ? "SCREENING CASCADE..." : "EXECUTE REAL-TIME FRAUD SCREENING"}</span>
            </button>

            {/* Decision & Latency Waterfall */}
            {detectionResult ? (
              <div className="flex flex-col gap-2.5">
                <div
                  className={`p-2.5 rounded border flex items-center justify-between ${
                    detectionResult.decision === "BLOCK"
                      ? "bg-rose-950/20 border-rose-800/40 text-rose-300"
                      : "bg-emerald-950/20 border-emerald-800/40 text-emerald-300"
                  }`}
                >
                  <div className="flex items-center gap-2 font-bold font-mono text-xs">
                    {detectionResult.decision === "BLOCK" ? <ShieldAlert size={16} className="text-rose-400" /> : <CheckCircle2 size={16} className="text-emerald-400" />}
                    <span>DECISION: {detectionResult.decision}</span>
                  </div>
                  <span className="font-mono text-xs font-semibold">
                    {(detectionResult.risk_score * 100).toFixed(1)}% RISK | {detectionResult.total_latency_ms.toFixed(2)}ms
                  </span>
                </div>

                {/* Segmented Micro-Progress Latency Waterfall */}
                <div className="bg-[#08090C] border border-[#1C2230] rounded p-2.5 text-xs flex flex-col gap-2">
                  <div className="flex items-center justify-between font-mono text-[10px]">
                    <span className="text-slate-400 uppercase font-semibold">Cascade Latency Waterfall</span>
                    <span className="text-sky-400 font-bold">{detectionResult.total_latency_ms.toFixed(2)}ms / 30.00ms SLA</span>
                  </div>

                  {/* Segmented Micro-Progress Bar */}
                  <div className="w-full bg-[#131722] h-3 rounded overflow-hidden flex border border-[#1C2230]">
                    {/* Tier 1 segment */}
                    <div
                      style={{ width: `${Math.min(100, (detectionResult.tier1_latency_ms / 30) * 100)}%` }}
                      className="bg-sky-500 h-full"
                      title={`Tier 1 (GBDT): ${detectionResult.tier1_latency_ms.toFixed(2)}ms`}
                    />
                    {/* Tier 2 segment */}
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

                {/* Clean Formatted SAR Audit Narrative */}
                {detectionResult.sar_report && (
                  <SarMarkdownViewer sarReport={detectionResult.sar_report} />
                )}
              </div>
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center text-center p-6 border border-dashed border-[#1C2230] rounded text-slate-500 text-xs">
                <Shield size={28} className="opacity-30 mb-2 text-slate-400" />
                <span className="font-mono text-[11px] text-slate-300">Ready for Switch Authorization</span>
                <span className="text-[10px] text-slate-500 max-w-xs mt-1">
                  Trigger screening above to inspect sub-30ms tier-cascade decision execution and regulatory narrative.
                </span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
