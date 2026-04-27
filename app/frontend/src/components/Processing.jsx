"import React, { useEffect, useState } from \"react\";

const BASE_STEPS = [
  { label: \"LOADING FIR DOCUMENT\", phase: \"ok\" },
  { label: \"RUNNING OCR EXTRACTION\", phase: \"ok\" },
  { label: \"PARSING NLP ENTITIES\", phase: \"ok\" },
  { label: \"BUILDING EVIDENCE GRAPH\", phase: \"ok\" },
  { label: \"ENGAGING REASONING ENGINE\", phase: \"active\" },
  { label: \"INFERRING MISSING EVENTS\", phase: \"active\" },
  { label: \"CONSTRUCTING TIMELINE\", phase: \"active\" },
];

export default function Processing({ done }) {
  const [visible, setVisible] = useState(0);

  useEffect(() => {
    setVisible(0);
    const id = setInterval(() => {
      setVisible((v) => (v < BASE_STEPS.length ? v + 1 : v));
    }, 420);
    return () => clearInterval(id);
  }, []);

  return (
    <section
      data-testid=\"processing-state\"
      className=\"section fade-up\"
    >
      <div className=\"section-title\">
        <span className=\"bar\" />
        <h2 className=\"section-label text-[15px]\">// Reasoning Engine</h2>
      </div>

      <div className=\"grid lg:grid-cols-5 gap-6 items-stretch\">
        {/* Terminal */}
        <div className=\"lg:col-span-3 terminal\">
          {BASE_STEPS.slice(0, visible).map((s, i) => {
            const isLast = i === visible - 1;
            const label = s.phase === \"ok\" || !isLast ? \"[OK]\" : \"[ACTIVE]\";
            const labelColor = s.phase === \"ok\" || !isLast ? \"text-[#5eeea6]\" : \"text-[#f6b84b]\";
            return (
              <div key={i} className=\"line\">
                <span className=\"prompt\">&gt;</span>
                <span className=\"flex-1 text-[#d7ffe2]\">
                  {s.label}
                  <span className=\"text-[#6b7280]\">
                    {\" \".padEnd(Math.max(2, 36 - s.label.length), \".\")}
                  </span>
                </span>
                <span className={`font-bold ${labelColor}`}>{label}</span>
              </div>
            );
          })}
          {visible >= BASE_STEPS.length && !done && (
            <div className=\"line mt-2\">
              <span className=\"prompt\">&gt;</span>
              <span className=\"text-[#a0f0b4] blink-cursor\">Awaiting Claude Sonnet 4.5 reasoning output</span>
            </div>
          )}
          {done && (
            <div className=\"line mt-2\">
              <span className=\"prompt\">&gt;</span>
              <span className=\"text-[#5eeea6]\">RECONSTRUCTION COMPLETE</span>
            </div>
          )}
        </div>

        {/* Ring */}
        <div className=\"lg:col-span-2 border border-[#1a1a2e] bg-[#0f0f1a] p-6 flex flex-col items-center justify-center gap-5\">
          <div className=\"relative\">
            <div className=\"ring-spin\" />
            <div className=\"absolute inset-0 flex items-center justify-center\">
              <svg width=\"40\" height=\"40\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"#c8a96e\" strokeWidth=\"1.5\">
                <path d=\"M21 21l-4.3-4.3\" />
                <circle cx=\"11\" cy=\"11\" r=\"7\" />
                <path d=\"M8 11h6M11 8v6\" />
              </svg>
            </div>
          </div>
          <div className=\"text-center\">
            <div className=\"font-stencil tracking-[0.3em] text-[#c8a96e] text-[13px]\">PROCESSING · ANALYSING EVIDENCE</div>
            <div className=\"font-mono text-[11px] text-[#6b7280] mt-2\">
              Do not navigate away. Case data is being committed to the evidence graph.
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
"