"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  ShieldAlert, 
  Layers, 
  Radio, 
  Cpu, 
  Network, 
  RefreshCw, 
  Command 
} from "lucide-react";

export default function Navbar() {
  const pathname = usePathname();

  const navTabs = [
    { label: "COMMAND CENTER", href: "/", icon: Layers, key: "1" },
    { label: "THREAT MATRIX", href: "/identify", icon: ShieldAlert, key: "2" },
    { label: "SIMULATION", href: "/generate", icon: Radio, key: "3" },
    { label: "DETECTION GRID", href: "/defend", icon: Cpu, key: "4" },
    { label: "TOPOLOGY GRAPH", href: "/graph", icon: Network, key: "5" },
    { label: "CO-EVOLUTION", href: "/loop", icon: RefreshCw, key: "6" },
  ];

  return (
    <header className="sticky top-0 z-50 h-12 bg-[#08090C]/95 backdrop-blur border-b border-[#1C2230] flex items-center justify-between px-3 text-xs select-none">
      {/* Left: Brand Emblem & Environmental Breadcrumbs */}
      <div className="flex items-center gap-3">
        <Link href="/" className="flex items-center gap-2 group">
          {/* Mastercard Interlocking Circles */}
          <div className="flex items-center -space-x-2">
            <div className="w-3.5 h-3.5 rounded-full bg-[#EB001B] opacity-95" />
            <div className="w-3.5 h-3.5 rounded-full bg-[#FF5F00] opacity-90" />
          </div>
          <div className="flex items-center gap-1.5 font-bold tracking-tight text-slate-100">
            <span>MASTERCARD</span>
            <span className="text-slate-600 font-mono font-normal">/</span>
            <span className="text-slate-300 font-semibold">AI DEFENSE LAB</span>
          </div>
        </Link>

        {/* Environmental Breadcrumbs */}
        <div className="hidden xl:flex items-center gap-2 pl-3 border-l border-[#1C2230] font-mono text-[10px] text-slate-500">
          <span>ENV:<span className="text-slate-300 ml-1 font-semibold">PROD-SIM-01</span></span>
          <span>•</span>
          <span>REGION:<span className="text-slate-300 ml-1">AP-SOUTH-1 (MUMBAI)</span></span>
          <span>•</span>
          <span>SLA:<span className="text-slate-300 ml-1">&lt;30MS</span></span>
        </div>
      </div>

      {/* Center: Command Navigation Tabs with Ember Underline */}
      <nav className="flex items-center h-full gap-1">
        {navTabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = pathname === tab.href;
          return (
            <Link
              key={tab.href}
              href={tab.href}
              className={`relative flex items-center h-full gap-1.5 px-3 text-[11px] font-medium transition-all ${
                isActive
                  ? "text-slate-100 font-semibold"
                  : "text-slate-400 hover:text-slate-200 hover:bg-[#131722]"
              }`}
            >
              <Icon size={13} className={isActive ? "text-[#FF5F00]" : "text-slate-500"} />
              <span>{tab.label}</span>
              <span className="hidden lg:inline text-[9px] font-mono text-slate-600 opacity-60 ml-0.5">
                [{tab.key}]
              </span>

              {/* Active Tab Underline in Mastercard Ember */}
              {isActive && (
                <div className="absolute bottom-0 left-0 right-0 h-[2px] bg-[#FF5F00]" />
              )}
            </Link>
          );
        })}
      </nav>

      {/* Right: Operational Status & Shortcuts */}
      <div className="flex items-center gap-2.5 font-mono text-[11px]">
        <div className="hidden sm:flex items-center gap-1.5 bg-[#0D1017] px-2 py-0.5 rounded border border-[#1C2230] text-slate-500 text-[10px]">
          <Command size={11} />
          <span>K</span>
          <span className="text-slate-300">SEARCH</span>
        </div>

        <div className="flex items-center gap-1.5 bg-[#10B981]/10 text-[#34D399] border border-[#10B981]/30 px-2 py-0.5 rounded text-[10px] font-semibold">
          <span className="w-1.5 h-1.5 rounded-full bg-[#10B981] animate-pulse" />
          <span>GRID ACTIVE</span>
          <span className="text-slate-600 font-normal">|</span>
          <span>&lt;30MS SLA</span>
        </div>
      </div>
    </header>
  );
}
