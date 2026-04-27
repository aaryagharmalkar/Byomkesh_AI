import React, { useState } from \"react\";

export default function AlternateScenarios({ scenarios = [] }) {
  const [openIdx, setOpenIdx] = useState(0);
  if (!scenarios.length) return null;
  return (
    <section data-testid=\"alternate-scenarios\" className=\"section\">
      <div className=\"section-title fade-up\">
        <span className=\"bar\" />
        <h2 className=\"section-label text-[15px]\">// Alternate Scenarios</h2>
      </div>

      <div className=\"grid md:grid-cols-2 gap-4\">
        {scenarios.map((s, i) => {
          const isOpen = openIdx === i;
          return (
            <button
              key={i}
              data-testid={`alt-scenario-${i}`}
              onClick={() => setOpenIdx(isOpen ? -1 : i)}
              className=\"text-left border border-dashed border-[#23233f] hover:border-[#c8a96e] bg-[#0b0b16] p-5 transition-all fade-up\"
              style={{ animationDelay: `${i * 0.12}s` }}
            >
              <div className=\"flex items-center justify-between\">
                <span className=\"section-label text-[11px]\">ALT · {String(i + 1).padStart(2, \"0\")}</span>
                <span className=\"badge badge-gold\">PROBABILITY · {s.probability}%</span>
              </div>
              <h3 className=\"mt-3 font-display text-[22px] leading-tight text-[#e8e8e8]\">
                {s.title}
              </h3>
              {isOpen && (
                <p className=\"mt-3 font-mono text-[12.5px] text-[#a1a7b3] leading-relaxed\">
                  <span className=\"text-[#f6b84b]\">//</span> {s.description}
                </p>
              )}
              <div className=\"mt-4 flex items-center gap-2\">
                <div className=\"conf-bar flex-1\">
                  <span
                    style={{ width: `${s.probability}%`, background: \"linear-gradient(90deg, #c8a96e, #8f7442)\" }}
                  />
                </div>
                <span className=\"font-mono text-[10px] text-[#6b7280]\">
                  {isOpen ? \"CLICK TO COLLAPSE\" : \"CLICK TO EXPAND\"}
                </span>
              </div>
            </button>
          );
        })}
      </div>
    </section>
  );
}
