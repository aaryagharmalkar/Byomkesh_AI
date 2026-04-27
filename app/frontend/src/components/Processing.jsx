import React, { useEffect, useState } from "react";

/* ------------------ Constants ------------------ */
const BASE_STEPS = [
  { label: "LOADING FIR DOCUMENT", phase: "ok" },
  { label: "RUNNING OCR EXTRACTION", phase: "ok" },
  { label: "PARSING NLP ENTITIES", phase: "ok" },
  { label: "BUILDING EVIDENCE GRAPH", phase: "ok" },
  { label: "ENGAGING REASONING ENGINE", phase: "active" },
  { label: "INFERRING MISSING EVENTS", phase: "active" },
  { label: "CONSTRUCTING TIMELINE", phase: "active" },
];

/* ------------------ Helpers ------------------ */
const getStatus = (step, isLastVisible) => {
  const isCompleted = step.phase === "ok" || !isLastVisible;

  return {
    label: isCompleted ? "[OK]" : "[ACTIVE]",
    color: isCompleted ? "text-[#5eeea6]" : "text-[#f6b84b]",
  };
};

/* ------------------ Component ------------------ */
export default function Processing({ done = false }) {
  const [visibleSteps, setVisibleSteps] = useState(0);

  useEffect(() => {
    setVisibleSteps(0);

    const interval = setInterval(() => {
      setVisibleSteps((prev) => {
        if (prev >= BASE_STEPS.length) {
          clearInterval(interval);
          return prev;
        }
        return prev + 1;
      });
    }, 420);

    return () => clearInterval(interval);
  }, []);

  const visibleList = BASE_STEPS.slice(0, visibleSteps);

  return (
    <section
      data-testid="processing-state"
      className="section fade-up"
    >
      {/* Header */}
      <div className="section-title">
        <span className="bar" />
        <h2 className="section-label text-[15px]">
          // Reasoning Engine
        </h2>
      </div>

      <div className="grid lg:grid-cols-5 gap-6 items-stretch">
        {/* Terminal */}
        <div className="lg:col-span-3 terminal">
          {visibleList.map((step, index) => {
            const isLast = index === visibleList.length - 1;
            const { label, color } = getStatus(step, isLast);

            return (
              <div key={index} className="line">
                <span className="prompt">&gt;</span>

                <span className="flex-1 text-[#d7ffe2]">
                  {step.label}
                  <span className="text-[#6b7280]">
                    {" ".padEnd(
                      Math.max(2, 36 - step.label.length),
                      "."
                    )}
                  </span>
                </span>

                <span className={`font-bold ${color}`}>
                  {label}
                </span>
              </div>
            );
          })}

          {/* Waiting State */}
          {visibleSteps >= BASE_STEPS.length && !done && (
            <div className="line mt-2">
              <span className="prompt">&gt;</span>
              <span className="text-[#a0f0b4] blink-cursor">
                Awaiting Claude Sonnet 4.5 reasoning output
              </span>
            </div>
          )}

          {/* Done State */}
          {done && (
            <div className="line mt-2">
              <span className="prompt">&gt;</span>
              <span className="text-[#5eeea6]">
                RECONSTRUCTION COMPLETE
              </span>
            </div>
          )}
        </div>

        {/* Processing Ring */}
        <div className="lg:col-span-2 border border-[#1a1a2e] bg-[#0f0f1a] p-6 flex flex-col items-center justify-center gap-5">
          <div className="relative">
            <div className="ring-spin" />

            <div className="absolute inset-0 flex items-center justify-center">
              <svg
                width="40"
                height="40"
                viewBox="0 0 24 24"
                fill="none"
                stroke="#c8a96e"
                strokeWidth="1.5"
              >
                <path d="M21 21l-4.3-4.3" />
                <circle cx="11" cy="11" r="7" />
                <path d="M8 11h6M11 8v6" />
              </svg>
            </div>
          </div>

          <div className="text-center">
            <div className="font-stencil tracking-[0.3em] text-[#c8a96e] text-[13px]">
              PROCESSING · ANALYSING EVIDENCE
            </div>

            <div className="font-mono text-[11px] text-[#6b7280] mt-2">
              Do not navigate away. Case data is being committed
              to the evidence graph.
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}