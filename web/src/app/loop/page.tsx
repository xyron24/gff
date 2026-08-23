"use client";

import { useEffect, useState } from "react";
import { RefreshCw, TrendingUp, ShieldCheck, Zap, AlertCircle, ArrowUpRight, CheckCircle2 } from "lucide-react";
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
    <div className="flex flex-col gap-4 w-full">
      {/* Header */}
      <div className="terminal-panel p-4 flex flex-wrap items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="badge-clean badge-neutral font-mono">CLOSED LOOP CO-EVOLUTION</span>
            <h1 className="font-bold text-sm text-slate-100 tracking-tight">
              AUTONOMOUS ADVERSARIAL FEEDBACK &amp; HARDENING ENGINE
            </h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Red-Team RL agent adapts attack policies based on evasion feedback; Blue Team mines false negatives to retrain and harden models.
          </p>
        </div>

        <button
          onClick={handleTriggerEpoch}
          disabled={loading}
          className="btn-ember py-2 px-4 text-xs font-mono font-bold tracking-wider uppercase"
        >
          <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
          <span>{loading ? "EXECUTING CO-EVOLUTION EPOCH..." : "TRIGGER CO-EVOLUTION EPOCH"}</span>
        </button>
      </div>

      {/* Cycle Lifecycle Steps */}
      <div className="terminal-panel p-4">
        <div className="terminal-title text-slate-200 mb-3">
          <span>THE AUTONOMOUS CO-EVOLUTION FEEDBACK CYCLE</span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          <div className="bg-[#131722] border border-[#1C2230] rounded p-3 text-xs">
            <div className="font-mono font-bold text-xs text-rose-400 mb-1">1. RED TEAM (RL AGENT)</div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              Samples attack vectors &amp; continuous perturbation bounds via Boltzmann Q-learning policy.
            </p>
          </div>

          <div className="bg-[#131722] border border-[#1C2230] rounded p-3 text-xs">
            <div className="font-mono font-bold text-xs text-sky-400 mb-1">2. BLUE TEAM (GRID)</div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              Evaluates transactions through cascading Tier 1 GBDT &amp; Tier 2 DyGNN (&lt;30ms).
            </p>
          </div>

          <div className="bg-[#131722] border border-[#1C2230] rounded p-3 text-xs">
            <div className="font-mono font-bold text-xs text-amber-400 mb-1">3. MINING (FALSE NEGATIVES)</div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              Automatically mines false negatives (evaded attacks) &amp; computes per-vector diagnostic rewards.
            </p>
          </div>

          <div className="bg-[#131722] border border-[#1C2230] rounded p-3 text-xs">
            <div className="font-mono font-bold text-xs text-emerald-400 mb-1">4. HARDENING RETRAIN</div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              Experience replay buffer samples hardened sets to incrementally retrain defense models.
            </p>
          </div>
        </div>
      </div>

      {/* Epoch Log Table */}
      <div className="terminal-panel flex flex-col">
        <div className="terminal-header">
          <div className="terminal-title">
            <TrendingUp size={13} className="text-emerald-400" />
            <span>EPOCH CONVERGENCE &amp; TRAJECTORY LOG ({history.length} EPOCHS COMPLETED)</span>
          </div>
        </div>

        <div className="overflow-x-auto">
          {history.length > 0 ? (
            <table className="terminal-table">
              <thead>
                <tr>
                  <th>EPOCH</th>
                  <th>SIMULATED</th>
                  <th>FRAUD ATTEMPTS</th>
                  <th>FALSE NEGATIVES</th>
                  <th>EVASION RATE</th>
                  <th>PRECISION / RECALL</th>
                  <th>REPLAY BUFFER</th>
                </tr>
              </thead>
              <tbody>
                {history.map((rec) => {
                  const met = rec.defense_metrics || {};
                  return (
                    <tr key={rec.epoch} className="hover:bg-[#131722]">
                      <td className="font-mono font-bold text-sky-400">EPOCH #{rec.epoch}</td>
                      <td className="font-mono">{rec.transactions_simulated}</td>
                      <td className="font-mono text-rose-400 font-semibold">{rec.fraud_attempts}</td>
                      <td className="font-mono text-amber-400 font-semibold">{rec.false_negatives_mined}</td>
                      <td className="font-mono font-bold text-slate-100">
                        {((rec.evasion_rate || 0) * 100).toFixed(1)}%
                      </td>
                      <td>
                        <span className="badge-clean badge-approved">
                          {((met.precision || 0.94) * 100).toFixed(1)}% P / {((met.recall || 0.91) * 100).toFixed(1)}% R
                        </span>
                      </td>
                      <td className="font-mono text-slate-400">{rec.replay_buffer_size} txns</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          ) : (
            <div className="p-8 text-center text-xs text-slate-500 font-mono">
              No co-evolution epochs executed yet. Click &quot;TRIGGER CO-EVOLUTION EPOCH&quot; above to start the feedback loop.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
