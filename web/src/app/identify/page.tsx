"use client";

import { useEffect, useState } from "react";
import { AlertTriangle, Shield, Search, X, CheckCircle, ChevronRight, FileCode } from "lucide-react";
import { fetchAttacks } from "@/lib/api";

export default function IdentifyPage() {
  const [attacks, setAttacks] = useState<any[]>([]);
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

  const categories = [
    { label: "All Vectors", value: "ALL" },
    { label: "Structuring", value: "structuring" },
    { label: "Voice Biometrics", value: "voice_biometric_spoofing" },
    { label: "Synthetic Identity", value: "identity_synthesis" },
    { label: "ISO 20022 Tampering", value: "metadata_tampering" },
    { label: "Behavioral Mimicry", value: "behavioral_mimicry" },
    { label: "Mule Rings", value: "graph_mule_orchestration" },
    { label: "Adversarial ML", value: "adversarial_perturbation" },
    { label: "Social Engineering", value: "social_engineering_bec" },
    { label: "Token Replay", value: "token_exploitation" },
    { label: "Account Takeover", value: "account_takeover" },
  ];

  const filteredAttacks = attacks.filter((atk) => {
    const matchesCat = selectedCategory === "ALL" || atk.category === selectedCategory;
    const matchesSearch =
      atk.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      atk.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      atk.genai_role.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCat && matchesSearch;
  });

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "28px" }}>
      {/* Header */}
      <div>
        <div className="badge badge-red" style={{ marginBottom: "10px" }}>
          PILLAR 1 • THREAT TAXONOMY
        </div>
        <h1 style={{ fontSize: "2rem", fontWeight: "800", letterSpacing: "-0.02em", marginBottom: "8px" }}>
          Emerging GenAI Payment Fraud Threat Vectors
        </h1>
        <p style={{ color: "var(--text-secondary)", fontSize: "0.95rem" }}>
          Comprehensive landscape mapping of 12 novel adversarial attack vectors spanning multiple payment rails, biometric gates, and ISO 20022 infrastructure.
        </p>
      </div>

      {/* Controls Bar */}
      <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "space-between", alignItems: "center", gap: "16px" }}>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
          {categories.map((cat) => (
            <button
              key={cat.value}
              onClick={() => setSelectedCategory(cat.value)}
              style={{
                padding: "6px 14px",
                borderRadius: "20px",
                fontSize: "0.8rem",
                fontWeight: 600,
                cursor: "pointer",
                border: selectedCategory === cat.value ? "1px solid var(--accent-cyan)" : "1px solid var(--border-color)",
                background: selectedCategory === cat.value ? "rgba(0, 212, 255, 0.15)" : "rgba(255, 255, 255, 0.03)",
                color: selectedCategory === cat.value ? "var(--accent-cyan)" : "var(--text-secondary)",
                transition: "all 0.2s ease",
              }}
            >
              {cat.label}
            </button>
          ))}
        </div>

        <div style={{ position: "relative", minWidth: "260px" }}>
          <Search size={16} color="var(--text-muted)" style={{ position: "absolute", left: "12px", top: "12px" }} />
          <input
            type="text"
            placeholder="Search attack vector or ID..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: "100%",
              padding: "10px 14px 10px 38px",
              borderRadius: "8px",
              background: "rgba(255, 255, 255, 0.04)",
              border: "1px solid var(--border-color)",
              color: "var(--text-primary)",
              fontSize: "0.88rem",
              outline: "none",
            }}
          />
        </div>
      </div>

      {/* Attack Cards Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(360px, 1fr))", gap: "20px" }}>
        {filteredAttacks.map((card) => (
          <div
            key={card.id}
            className="glass-card"
            style={{
              padding: "24px",
              display: "flex",
              flexDirection: "column",
              justifyContent: "space-between",
              cursor: "pointer",
            }}
            onClick={() => setActiveModalCard(card)}
          >
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "14px" }}>
                <span style={{ fontFamily: "var(--font-mono)", fontSize: "0.8rem", color: "var(--accent-cyan)", fontWeight: 700 }}>
                  {card.id}
                </span>
                <span className={card.severity === "CRITICAL" ? "badge badge-red" : "badge badge-amber"}>
                  {card.severity}
                </span>
              </div>

              <h3 style={{ fontSize: "1.15rem", fontWeight: "700", marginBottom: "8px" }}>
                {card.name}
              </h3>

              <div style={{ display: "flex", gap: "8px", marginBottom: "14px" }}>
                <span className="badge badge-purple" style={{ fontSize: "0.7rem" }}>
                  {card.channel.replace("_", " ")}
                </span>
                <span className="badge badge-cyan" style={{ fontSize: "0.7rem" }}>
                  {card.iso_mapping.message_type}
                </span>
              </div>

              <p style={{ color: "var(--text-secondary)", fontSize: "0.85rem", lineHeight: "1.5", marginBottom: "18px" }}>
                {card.genai_role}
              </p>
            </div>

            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", paddingTop: "14px", borderTop: "1px solid var(--border-color)" }}>
              <span style={{ fontSize: "0.78rem", color: "var(--text-muted)" }}>
                {card.kill_chain.length} Kill Chain Steps • {card.detection_signals.length} Signals
              </span>
              <span style={{ color: "var(--accent-cyan)", fontSize: "0.82rem", fontWeight: 600, display: "flex", alignItems: "center" }}>
                View Details <ChevronRight size={14} />
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Modal Detail View */}
      {activeModalCard && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: "rgba(0, 0, 0, 0.8)",
            backdropFilter: "blur(8px)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 1000,
            padding: "20px",
          }}
          onClick={() => setActiveModalCard(null)}
        >
          <div
            className="glass-card"
            style={{
              maxWidth: "800px",
              width: "100%",
              maxHeight: "90vh",
              overflowY: "auto",
              padding: "36px",
              background: "#0d1322",
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "18px" }}>
              <div>
                <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "6px" }}>
                  <span style={{ fontFamily: "var(--font-mono)", fontSize: "0.9rem", color: "var(--accent-cyan)", fontWeight: 700 }}>
                    {activeModalCard.id}
                  </span>
                  <span className={activeModalCard.severity === "CRITICAL" ? "badge badge-red" : "badge badge-amber"}>
                    {activeModalCard.severity}
                  </span>
                </div>
                <h2 style={{ fontSize: "1.6rem", fontWeight: "800" }}>{activeModalCard.name}</h2>
              </div>
              <button
                onClick={() => setActiveModalCard(null)}
                style={{ background: "transparent", border: "none", color: "var(--text-muted)", cursor: "pointer" }}
              >
                <X size={24} />
              </button>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "22px" }}>
              <div>
                <h4 style={{ fontSize: "0.9rem", color: "var(--accent-cyan)", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "8px" }}>
                  Mechanics & Attack Description
                </h4>
                <p style={{ color: "var(--text-secondary)", fontSize: "0.92rem", lineHeight: "1.6" }}>
                  {activeModalCard.attack_description}
                </p>
              </div>

              {/* Kill Chain */}
              <div>
                <h4 style={{ fontSize: "0.9rem", color: "var(--accent-purple)", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "12px" }}>
                  4-Stage Kill Chain Lifecycle
                </h4>
                <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                  {activeModalCard.kill_chain.map((step: any) => (
                    <div
                      key={step.step_number}
                      style={{
                        padding: "14px",
                        borderRadius: "8px",
                        background: "rgba(255, 255, 255, 0.03)",
                        border: "1px solid var(--border-color)",
                      }}
                    >
                      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "4px" }}>
                        <span style={{ fontWeight: 700, fontSize: "0.88rem", color: "var(--text-primary)" }}>
                          Step {step.step_number}: {step.stage_name}
                        </span>
                        <span className="badge badge-purple" style={{ fontSize: "0.7rem" }}>
                          {step.genai_technique}
                        </span>
                      </div>
                      <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
                        {step.adversary_action}
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Detection Signals */}
              <div>
                <h4 style={{ fontSize: "0.9rem", color: "var(--accent-green)", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "12px" }}>
                  Telemetry Detection Signals
                </h4>
                <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                  {activeModalCard.detection_signals.map((sig: any) => (
                    <div
                      key={sig.signal_id}
                      style={{
                        padding: "14px",
                        borderRadius: "8px",
                        background: "rgba(16, 185, 129, 0.05)",
                        border: "1px solid rgba(16, 185, 129, 0.2)",
                      }}
                    >
                      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "4px" }}>
                        <span style={{ fontWeight: 700, fontSize: "0.85rem", color: "var(--accent-green)" }}>
                          {sig.signal_id} • {sig.recommended_layer}
                        </span>
                      </div>
                      <p style={{ fontSize: "0.85rem", color: "var(--text-primary)", marginBottom: "4px" }}>
                        {sig.indicator}
                      </p>
                      <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                        Source: {sig.telemetry_source}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* ISO Mapping */}
              <div style={{ padding: "16px", borderRadius: "8px", background: "rgba(0, 212, 255, 0.05)", border: "1px solid rgba(0, 212, 255, 0.2)" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "6px" }}>
                  <FileCode size={16} color="var(--accent-cyan)" />
                  <span style={{ fontWeight: 700, fontSize: "0.85rem", color: "var(--accent-cyan)" }}>
                    ISO 20022 PAYLOAD MAPPING: {activeModalCard.iso_mapping.message_type}
                  </span>
                </div>
                <p style={{ fontSize: "0.82rem", color: "var(--text-secondary)" }}>
                  {activeModalCard.iso_mapping.tampering_pattern}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
