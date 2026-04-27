import React, { useEffect, useState } from "react";
import { ShieldLogo } from "./ShieldLogo";

/* ------------------ Helpers ------------------ */
const DEFAULT_CASE = "CASE #2024-MH-4471";
const DEFAULT_OFFICER = "INSP. SHARMA";

const formatUTC = (date) =>
  new Intl.DateTimeFormat("en-GB", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    timeZone: "UTC",
    hour12: false,
  }).format(date);

/* ------------------ Component ------------------ */
export default function TopNav({
  caseId = DEFAULT_CASE,
  officer = DEFAULT_OFFICER,
}) {
  const [time, setTime] = useState(() => new Date());

  useEffect(() => {
    const interval = setInterval(() => {
      setTime(new Date());
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const timeString = formatUTC(time);

  return (
    <header
      data-testid="top-nav"
      className="w-full border-b border-[#1a1a2e] bg-[#07070c]/90 backdrop-blur-sm sticky top-0 z-50"
      aria-label="Top navigation"
    >
      <div className="max-w-[1280px] mx-auto px-6 py-3 flex items-center justify-between gap-6">
        
        {/* Left: Logo */}
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 shrink-0">
            <ShieldLogo className="w-full h-full" />
          </div>

          <div className="flex flex-col leading-tight">
            <span
              data-testid="sentinel-wordmark"
              className="glitch font-display text-[22px] font-bold tracking-[0.22em] text-[#e8e8e8]"
              data-text="SENTINEL"
            >
              SENTINEL
            </span>

            <span className="font-stencil text-[10px] text-[#c8a96e]">
              Forensic · AI · Division
            </span>
          </div>
        </div>

        {/* Center: Case Info */}
        <div className="hidden md:flex items-center gap-3 px-4 py-1.5 border border-[#1a1a2e] bg-[#0f0f1a]">
          <span className="dot dot-amber" />

          <span
            data-testid="case-id"
            className="font-mono text-xs tracking-[0.2em] text-[#e8e8e8]"
          >
            {caseId}
          </span>

          <span className="font-mono text-xs text-[#6b7280]">
            {timeString} UTC
          </span>
        </div>

        {/* Right: Status */}
        <div className="flex items-center gap-4">
          
          {/* Active Case */}
          <div
            data-testid="active-case-badge"
            className="flex items-center gap-2 px-3 py-1.5 border border-[#e5393566] bg-[#e5393510]"
          >
            <span className="w-2.5 h-2.5 rounded-full bg-[#e53935] pulse-red" />
            <span className="font-stencil text-[11px] text-[#ff7a77]">
              Active Case
            </span>
          </div>

          {/* Officer */}
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 border border-[#1a1a2e] bg-[#0f0f1a]">
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#c8a96e"
              strokeWidth="1.8"
            >
              <circle cx="12" cy="8" r="4" />
              <path d="M4 21c0-4.4 3.6-8 8-8s8 3.6 8 8" />
            </svg>

            <span
              data-testid="officer-name"
              className="font-stencil text-[11px] text-[#e3cb96]"
            >
              {officer}
            </span>
          </div>

          {/* Secure Status */}
          <div className="hidden md:flex items-center gap-2">
            <span className="dot dot-green" />
            <span className="font-stencil text-[11px] text-[#5eeea6]">
              Secure
            </span>
          </div>

        </div>
      </div>
    </header>
  );
}