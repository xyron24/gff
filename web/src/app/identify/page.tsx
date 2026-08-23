"use client";

import { useEffect, useState } from "react";
import { 
  ShieldAlert, 
  Search, 
  X, 
  ChevronRight, 
  FileCode, 
  Activity, 
  AlertTriangle, 
  ArrowRight,
  Filter
} from "lucide-react";
import { fetchAttacks } from "@/lib/api";

export default function IdentifyPage() {
  const [attacks, setAttacks] = useState<any[]>([]);
  const [selectedChannel, setSelectedChannel] = useState<string>("ALL");
  const [selectedCategory, setSelectedCategory] = useState<string>("ALL");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [activeModalCard, setActiveModalCard] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await fetchAttacks();
        setAttacks(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const channels = [
    { label: "All Payment Channels", value: "ALL" },
    { label: "Card-Not-Present (CNP)", value: "card_not_present" },
    { label: "SWIFT / RTGS Wire", value: "wire_swift" },
    { label: "Real-Time P2P / RTP", value: "p2p_realtime" },
    { label: "Point of Sale (POS)", value: "card_present_pos" },
    { label: "Open Banking API", value: "open_banking_pisp" },
    { label: "Mobile NFC / Wallet", value: "mobile_nfc" },
  ];

  const categories = [
    { label: "All Categories", value: "ALL" },
    { label: "Structuring / Smurfing", value: "structuring" },
    { label: "Voice Spoofing", value: "voice_biometric_spoofing" },
    { label: "Synthetic ID Synthesis", value: "identity_synthesis" },
    { label: "ISO 20022 Tampering", value: "metadata_tampering" },
    { label: "Behavioral Biometric Mimicry", value: "behavioral_mimicry" },
    { label: "Mule Ring Orchestration", value: "graph_mule_orchestration" },
    { label: "Adversarial Feature Perturbation", value: "adversarial_perturbation" },
    { label: "Social Engineering / BEC", value: "social_engineering_bec" },
    { label: "Token Replay Exploitation", value: "token_exploitation" },
    { label: "Real-Time Account Takeover", value: "account_takeover" },
  ];

  const filteredAttacks = attacks.filter((atk) => {
    const matchesChan = selectedChannel === "ALL" || atk.channel === selectedChannel;
    const matchesCat = selectedCategory === "ALL" || atk.category === selectedCategory;
    const matchesSearch =
      atk.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      atk.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      atk.genai_role.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesChan && matchesCat && matchesSearch;
  });

  return (
    <div className="flex flex-col gap-4 w-full">
      {/* 1. Header & Integrated Filter Toolbar */}
      <div className="terminal-panel p-4 flex flex-col gap-3">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[#1C2230] pb-3">
          <div>
            <div className="flex items-center gap-2">
              <span className="badge-clean badge-threat font-mono">PILLAR 1: IDENTIFY</span>
              <h1 className="font-bold text-sm text-slate-100 tracking-tight">
                ADVERSARIAL PAYMENT FRAUD THREAT MATRIX
              </h1>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Systematic operational landscape mapping of 12 novel Generative AI attack vectors across retail and wholesale payment rails.
            </p>
          </div>

          <div className="flex items-center gap-2 font-mono text-xs text-slate-400">
            <span className="bg-[#131722] px-2.5 py-1 rounded border border-[#1C2230]">
              SHOWING <strong className="text-slate-100">{filteredAttacks.length}</strong> OF <strong className="text-slate-100">{attacks.length || 12}</strong> VECTORS
            </span>
          </div>
        </div>

        {/* Clean Filter Controls */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 items-center">
          {/* Payment Channel Dropdown */}
          <div>
            <label className="text-[10px] font-mono text-slate-500 uppercase tracking-wider block mb-1">
              PAYMENT CHANNEL FILTER
            </label>
            <select
              value={selectedChannel}
              onChange={(e) => setSelectedChannel(e.target.value)}
              className="w-full bg-[#131722] border border-[#1C2230] rounded px-3 py-1.5 text-xs font-mono text-slate-200 outline-none focus:border-[#FF5F00]"
            >
              {channels.map((c) => (
                <option key={c.value} value={c.value}>{c.label}</option>
              ))}
            </select>
          </div>

          {/* Category Dropdown */}
          <div>
            <label className="text-[10px] font-mono text-slate-500 uppercase tracking-wider block mb-1">
              ATTACK CATEGORY FILTER
            </label>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-full bg-[#131722] border border-[#1C2230] rounded px-3 py-1.5 text-xs font-mono text-slate-200 outline-none focus:border-[#FF5F00]"
            >
              {categories.map((c) => (
                <option key={c.value} value={c.value}>{c.label}</option>
              ))}
            </select>
          </div>

          {/* Search Input */}
          <div>
            <label className="text-[10px] font-mono text-slate-500 uppercase tracking-wider block mb-1">
              QUICK SEARCH
            </label>
            <div className="relative">
              <Search size={13} className="absolute left-2.5 top-2.5 text-slate-500" />
              <input
                type="text"
                placeholder="Search by vector ID, name, or keyword..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-[#131722] border border-[#1C2230] rounded pl-8 pr-3 py-1.5 text-xs font-mono text-slate-200 outline-none focus:border-[#FF5F00]"
              />
            </div>
          </div>
        </div>
      </div>

      {/* 2. Spacious 3-Column Threat Matrix Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {filteredAttacks.map((card) => (
          <div
            key={card.id}
            onClick={() => setActiveModalCard(card)}
            className="terminal-panel p-5 flex flex-col justify-between cursor-pointer hover:border-[#2D3748] hover:bg-[#131722] transition-all space-y-3"
          >
            {/* Header: Monospace ID + Ruby/Amber Severity Badge */}
            <div>
              <div className="flex items-center justify-between font-mono text-xs mb-2">
                <span className="font-mono text-xs font-semibold text-slate-400">{card.id}</span>
                <span
                  className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                    card.severity === "CRITICAL"
                      ? "bg-[#991B1B]/20 text-[#F87171] border border-[#991B1B]/40"
                      : "bg-[#92400E]/20 text-[#FBBF24] border border-[#92400E]/40"
                  }`}
                >
                  {card.severity}
                </span>
              </div>

              {/* Title */}
              <h3 className="text-sm font-semibold text-slate-100 tracking-tight mb-2">
                {card.name}
              </h3>

              {/* Micro-Badges */}
              <div className="flex flex-wrap items-center gap-1.5 mb-3">
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#131722] border border-[#232936] text-slate-300">
                  {card.channel.replace(/_/g, " ")}
                </span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#131722] border border-[#232936] text-sky-400">
                  {card.iso_mapping.message_type}
                </span>
              </div>

              {/* Description */}
              <p className="text-xs leading-relaxed text-slate-400 line-clamp-3">
                {card.genai_role}
              </p>
            </div>

            {/* Footer */}
            <div className="border-t border-[#1A1F2C] pt-3 mt-3 flex items-center justify-between font-mono text-[11px]">
              <span className="text-slate-500">
                {card.kill_chain.length} Kill Chain Steps • {card.detection_signals.length} Signals
              </span>
              <span className="text-[#FF5F00] font-semibold flex items-center gap-1 hover:underline">
                <span>View Details</span> <ChevronRight size={12} />
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* 3. Modal Deep-Dive Inspector */}
      {activeModalCard && (
        <div
          className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4"
          onClick={() => setActiveModalCard(null)}
        >
          <div
            className="terminal-panel max-w-3xl w-full max-h-[85vh] overflow-y-auto p-5 bg-[#0D1017]"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="flex items-start justify-between border-b border-[#1C2230] pb-3 mb-3">
              <div>
                <div className="flex items-center gap-2 font-mono text-xs mb-1">
                  <span className="text-sky-400 font-bold">{activeModalCard.id}</span>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                    activeModalCard.severity === "CRITICAL"
                      ? "bg-[#991B1B]/20 text-[#F87171] border border-[#991B1B]/40"
                      : "bg-[#92400E]/20 text-[#FBBF24] border border-[#92400E]/40"
                  }`}>
                    {activeModalCard.severity}
                  </span>
                  <span className="badge-clean badge-neutral">
                    {activeModalCard.channel}
                  </span>
                </div>
                <h2 className="text-base font-bold text-slate-100">{activeModalCard.name}</h2>
              </div>
              <button onClick={() => setActiveModalCard(null)} className="text-slate-500 hover:text-slate-200">
                <X size={18} />
              </button>
            </div>

            <div className="flex flex-col gap-4 text-xs">
              {/* Description */}
              <div>
                <div className="font-mono text-[10px] text-slate-500 font-bold uppercase tracking-wider mb-1">
                  Attack Description &amp; Mechanics
                </div>
                <p className="text-slate-300 text-xs leading-relaxed">
                  {activeModalCard.attack_description}
                </p>
              </div>

              {/* 4-Stage Kill Chain */}
              <div>
                <div className="font-mono text-[10px] text-purple-400 font-bold uppercase tracking-wider mb-2">
                  4-Stage Attack Lifecycle
                </div>
                <div className="space-y-2">
                  {activeModalCard.kill_chain.map((st: any) => (
                    <div key={st.step_number} className="bg-[#131722] border border-[#1C2230] rounded p-3 text-xs">
                      <div className="flex items-center justify-between font-mono text-xs text-slate-400 mb-1">
                        <span className="font-bold text-slate-200">STAGE {st.step_number}: {st.stage_name}</span>
                        <span className="badge-clean badge-neutral">{st.genai_technique}</span>
                      </div>
                      <p className="text-slate-300 text-[11px] leading-relaxed">{st.adversary_action}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Detection Signals */}
              <div>
                <div className="font-mono text-[10px] text-emerald-400 font-bold uppercase tracking-wider mb-2">
                  Telemetry Detection Signals
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {activeModalCard.detection_signals.map((sig: any) => (
                    <div key={sig.signal_id} className="bg-emerald-950/10 border border-emerald-800/30 rounded p-3 text-xs">
                      <div className="font-mono text-[11px] text-emerald-400 font-bold mb-1">
                        {sig.signal_id} • {sig.recommended_layer}
                      </div>
                      <p className="text-slate-200 text-[11px] mb-1.5">{sig.indicator}</p>
                      <span className="font-mono text-[10px] text-slate-500">SRC: {sig.telemetry_source}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* ISO Mapping */}
              <div className="bg-[#08090C] border border-[#1C2230] rounded p-3 font-mono text-xs">
                <div className="flex items-center gap-1.5 text-sky-400 font-bold mb-1">
                  <FileCode size={13} />
                  <span>ISO 20022 PAYLOAD MAPPING: {activeModalCard.iso_mapping.message_type}</span>
                </div>
                <p className="text-slate-400 text-[11px]">{activeModalCard.iso_mapping.tampering_pattern}</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
