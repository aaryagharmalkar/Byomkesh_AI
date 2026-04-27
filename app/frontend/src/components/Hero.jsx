import React, { useEffect, useRef, useState } from "react";

/* ------------------ Typewriter Hook ------------------ */
function useTypewriter(text, speed = 45, startDelay = 200) {
  const [typedText, setTypedText] = useState("");
  const [isDone, setIsDone] = useState(false);

  const intervalRef = useRef(null);
  const timeoutRef = useRef(null);

  useEffect(() => {
    setTypedText("");
    setIsDone(false);

    let index = 0;

    timeoutRef.current = setTimeout(() => {
      intervalRef.current = setInterval(() => {
        index += 1;
        setTypedText(text.slice(0, index));

        if (index >= text.length) {
          clearInterval(intervalRef.current);
          setIsDone(true);
        }
      }, speed);
    }, startDelay);

    return () => {
      clearTimeout(timeoutRef.current);
      clearInterval(intervalRef.current);
    };
  }, [text, speed, startDelay]);

  return { typedText, isDone };
}

/* ------------------ Constants ------------------ */
const STATS = [
  { key: "MODEL", value: "Claude Sonnet 4.5" },
  { key: "CASES RECONSTRUCTED", value: "12,847" },
  { key: "AVG. CONFIDENCE", value: "81.4%" },
  { key: "CLASSIFICATION", value: "RESTRICTED" },
];

/* ------------------ Component ------------------ */
export default function Hero({
  onUploadClick,
  onViewCasesClick,
}) {
  const { typedText, isDone } = useTypewriter(
    "RECONSTRUCT. REASON. REVEAL.",
    55,
    300
  );

  return (
    <section
      data-testid="hero-section"
      className="relative overflow-hidden border-b border-[#1a1a2e]"
    >
      {/* Background SVG */}
      <svg
        className="absolute inset-0 w-full h-full opacity-40 pointer-events-none"
        xmlns="http://www.w3.org/2000/svg"
        aria-hidden="true"
      >
        <defs>
          <pattern
            id="dots"
            width="36"
            height="36"
            patternUnits="userSpaceOnUse"
          >
            <circle
              cx="1"
              cy="1"
              r="1"
              fill="rgba(200,169,110,0.18)"
            />
          </pattern>
        </defs>

        <rect width="100%" height="100%" fill="url(#dots)" />

        {/* Strings */}
        <line x1="5%" y1="20%" x2="70%" y2="80%" stroke="rgba(229,57,53,0.35)" strokeWidth="0.6" />
        <line x1="80%" y1="10%" x2="15%" y2="70%" stroke="rgba(79,195,247,0.25)" strokeWidth="0.5" />
        <line x1="30%" y1="90%" x2="90%" y2="30%" stroke="rgba(200,169,110,0.35)" strokeWidth="0.5" />

        {/* Pins */}
        <circle cx="5%" cy="20%" r="3" fill="#c8a96e" />
        <circle cx="70%" cy="80%" r="3" fill="#c8a96e" />
        <circle cx="80%" cy="10%" r="3" fill="#4fc3f7" />
        <circle cx="15%" cy="70%" r="3" fill="#4fc3f7" />
        <circle cx="30%" cy="90%" r="3" fill="#e53935" />
        <circle cx="90%" cy="30%" r="3" fill="#e53935" />
      </svg>

      {/* Content */}
      <div className="max-w-[1280px] mx-auto px-6 py-24 md:py-32 relative">
        <div className="fade-up stagger-1">
          <span className="section-label">
            // Operation Room · Command Center
          </span>
        </div>

        {/* Heading */}
        <h1
          data-testid="hero-heading"
          aria-live="polite"
          className={`mt-5 font-display font-bold text-[42px] sm:text-[56px] lg:text-[84px] leading-[0.95] text-[#e8e8e8] ${
            !isDone ? "type-caret" : ""
          }`}
        >
          {typedText || "\u00A0"}
        </h1>

        {/* Description */}
        <p className="mt-6 font-mono text-[#a1a7b3] max-w-[640px] text-sm md:text-base fade-up stagger-3">
          <span className="text-[#c8a96e]">//</span>{" "}
          AI-Powered Forensic Timeline Reconstruction Engine — trained on
          thousands of closed cases to surface stated facts, infer missing
          links, and quantify every conclusion.
        </p>

        {/* Actions */}
        <div className="mt-10 flex flex-wrap gap-4 fade-up stagger-4">
          <button
            data-testid="hero-upload-btn"
            onClick={onUploadClick}
            className="btn-gold px-7 py-3 text-sm"
          >
            Upload FIR Document
          </button>

          <button
            data-testid="hero-view-cases-btn"
            onClick={onViewCasesClick}
            className="btn-outline-blue px-7 py-3 text-sm"
          >
            View Active Cases
          </button>
        </div>

        {/* Stats */}
        <div className="mt-14 grid grid-cols-2 md:grid-cols-4 gap-4 fade-up stagger-5">
          {STATS.map(({ key, value }) => (
            <div
              key={key}
              className="border border-[#1a1a2e] bg-[#0f0f1a]/60 px-4 py-3"
            >
              <div className="font-stencil text-[10px] text-[#c8a96e]">
                {key}
              </div>
              <div className="font-mono text-sm mt-1 text-[#e8e8e8]">
                {value}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}