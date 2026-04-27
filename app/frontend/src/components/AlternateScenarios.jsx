import React, { useState } from "react";

export default function AlternateScenarios({ scenarios = [] }) {
  const [openIndex, setOpenIndex] = useState(null);

  if (!scenarios?.length) return null;

  const toggleScenario = (index) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  return (
    <section data-testid="alternate-scenarios" className="section">
      {/* Header */}
      <div className="section-title fade-up">
        <span className="bar" />
        <h2 className="section-label text-[15px]">
          // Alternate Scenarios
        </h2>
      </div>

      {/* Grid */}
      <div className="grid md:grid-cols-2 gap-4">
        {scenarios.map((scenario, index) => {
          const isOpen = openIndex === index;

          return (
            <button
              key={index}
              data-testid={`alt-scenario-${index}`}
              onClick={() => toggleScenario(index)}
              className="text-left border border-dashed border-[#23233f] hover:border-[#c8a96e] bg-[#0b0b16] p-5 transition-all fade-up"
              style={{ animationDelay: `${index * 0.12}s` }}
            >
              {/* Top Row */}
              <div className="flex items-center justify-between">
                <span className="section-label text-[11px]">
                  ALT · {String(index + 1).padStart(2, "0")}
                </span>
                <span className="badge badge-gold">
                  PROBABILITY · {scenario.probability}%
                </span>
              </div>

              {/* Title */}
              <h3 className="mt-3 font-display text-[22px] leading-tight text-[#e8e8e8]">
                {scenario.title}
              </h3>

              {/* Description */}
              {isOpen && (
                <p className="mt-3 font-mono text-[12.5px] text-[#a1a7b3] leading-relaxed">
                  <span className="text-[#f6b84b]">//</span>{" "}
                  {scenario.description}
                </p>
              )}

              {/* Progress Bar */}
              <div className="mt-4 flex items-center gap-2">
                <div className="conf-bar flex-1">
                  <span
                    style={{
                      width: `${scenario.probability}%`,
                      background:
                        "linear-gradient(90deg, #c8a96e, #8f7442)",
                    }}
                  />
                </div>

                <span className="font-mono text-[10px] text-[#6b7280]">
                  {isOpen ? "CLICK TO COLLAPSE" : "CLICK TO EXPAND"}
                </span>
              </div>
            </button>
          );
        })}
      </div>
    </section>
  );
}