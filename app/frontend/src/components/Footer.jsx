import React from "react";

export default function Footer({
  caseId = "CASE #2024-MH-4471",
}) {
  return (
    <footer
      data-testid="site-footer"
      className="relative mt-16 border-t-[2px] border-[#c8a96e] bg-[#05050a]"
      aria-label="Application footer"
    >
      <div className="max-w-[1280px] mx-auto px-6 py-6 flex flex-col md:flex-row items-center justify-between gap-3">
        
        {/* Left */}
        <div className="font-stencil text-[11px] tracking-[0.25em] text-[#e3cb96]">
          Sentinel · Forensic AI Division
        </div>

        {/* Center */}
        <div className="font-mono text-[11px] text-[#6b7280]">
          Ref: {caseId}
        </div>

        {/* Right */}
        <div className="font-stencil text-[11px] tracking-[0.25em] text-[#ff7a77]">
          Restricted // Law Enforcement Only
        </div>

      </div>
    </footer>
  );
}