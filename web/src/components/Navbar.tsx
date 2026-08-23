"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Shield, Radio, Cpu, Network, RefreshCw, AlertTriangle, Layers } from "lucide-react";

export default function Navbar() {
  const pathname = usePathname();

  const navItems = [
    { name: "Command Center", href: "/", icon: Layers },
    { name: "Threat Taxonomy", href: "/identify", icon: AlertTriangle },
    { name: "Simulation Engine", href: "/generate", icon: Radio },
    { name: "Detection Grid", href: "/defend", icon: Shield },
    { name: "Mule Ring Graph", href: "/graph", icon: Network },
    { name: "Co-Evolution", href: "/loop", icon: RefreshCw },
  ];

  return (
    <header style={{
      borderBottom: "1px solid var(--border-color)",
      background: "rgba(7, 10, 19, 0.85)",
      backdropFilter: "blur(12px)",
      position: "sticky",
      top: 0,
      zIndex: 100,
    }}>
      <div style={{
        maxWidth: "1400px",
        margin: "0 auto",
        padding: "0 24px",
        height: "70px",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
      }}>
        {/* Brand Logo */}
        <Link href="/" style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <div style={{
            width: "38px",
            height: "38px",
            borderRadius: "10px",
            background: "linear-gradient(135deg, #eb001b, #f79e1b)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            boxShadow: "0 4px 14px rgba(235, 0, 27, 0.4)",
          }}>
            <Shield size={22} color="#fff" />
          </div>
          <div>
            <div style={{ fontSize: "1.1rem", fontWeight: "800", letterSpacing: "-0.02em", display: "flex", alignItems: "center", gap: "6px" }}>
              MASTERCARD <span style={{ color: "var(--accent-cyan)", fontWeight: "600", fontSize: "0.85rem", background: "rgba(0,212,255,0.1)", padding: "2px 6px", borderRadius: "4px" }}>AI DEFENSE LAB</span>
            </div>
            <div style={{ fontSize: "0.7rem", color: "var(--text-muted)", letterSpacing: "0.04em" }}>
              GLOBAL FINTECH FEST 2026 • ADVERSARIAL DEFENSE GRID
            </div>
          </div>
        </Link>

        {/* Navigation Tabs */}
        <nav style={{ display: "flex", gap: "6px" }}>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                  padding: "8px 14px",
                  borderRadius: "8px",
                  fontSize: "0.88rem",
                  fontWeight: isActive ? 700 : 500,
                  color: isActive ? "var(--accent-cyan)" : "var(--text-secondary)",
                  background: isActive ? "rgba(0, 212, 255, 0.08)" : "transparent",
                  border: isActive ? "1px solid rgba(0, 212, 255, 0.25)" : "1px solid transparent",
                  transition: "all 0.2s ease",
                }}
              >
                <Icon size={16} />
                {item.name}
              </Link>
            );
          })}
        </nav>

        {/* Right Status Badge */}
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <div className="badge badge-green" style={{ gap: "8px" }}>
            <span className="status-dot" />
            GRID ACTIVE • &lt;30MS
          </div>
        </div>
      </div>
    </header>
  );
}
