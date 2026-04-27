import React, { useState } from "react";

/* ------------------ Helpers ------------------ */
const getConfidenceMeta = (confidence = "") => {
  switch (confidence.toUpperCase()) {
    case "HIGH":
      return { className: "badge badge-green", percent: 90, color: "#00e676" };
    case "MEDIUM":
      return { className: "badge badge-amber", percent: 62, color: "#f6b84b" };
    case "LOW":
      return { className: "badge badge-red", percent: 30, color: "#e53935" };
    default:
      return { className: "badge badge-muted", percent: 50, color: "#6b7280" };
  }
};

/* ------------------ Event Card ------------------ */
function EventCard({ event, index }) {
  const [isOpen, setIsOpen] = useState(false);

  const source = (event.source || "").toUpperCase();
  const isStated = source === "STATED";

  const meta = getConfidenceMeta(event.confidence);
  const stagger = Math.min(6, (index % 6) + 1);

  const stepNumber = String(event.step || index + 1).padStart(2, "0");

  return (
    <div
      data-testid={`timeline-event-${index}`}
      className="relative pl-14 pb-10"
      style={{
        animation: `fade-up 0.7s cubic-bezier(.2,.8,.2,1) both ${
          0.05 + index * 0.18
        }s`,
      }}
    >
      {/* Timeline Node */}
      <div className="absolute left-[9px] top-1">
        <span
          className={`block w-[24px] h-[24px] rounded-full border-2 ${
            isStated
              ? "border-[#4fc3f7] bg-[#4fc3f730] pulse-blue"
              : "border-dashed border-[#f6b84b] pulse-amber"
          }`}
          title={source || "UNKNOWN"}
        />
      </div>

      {/* Card */}
      <article
        className={`card-noir p-5 border-l-2 left-flash stagger-${stagger}`}
        style={{
          borderLeftColor: isStated ? "#4fc3f7" : "#f6b84b",
        }}
      >
        {/* Header */}
        <div className="flex items-center justify-between flex-wrap gap-2">
          <div className="flex items-center gap-3">
            <span className="font-stencil text-[11px] text-[#c8a96e]">
              STEP {stepNumber}
            </span>

            {event.timestamp && (
              <span className="font-mono text-[12px] text-[#87d6fa]">
                {event.timestamp}
              </span>
            )}
          </div>

          <div className="flex items-center gap-2">
            <span
              className={
                isStated ? "badge badge-blue" : "badge badge-amber"
              }
            >
              {source || "—"}
            </span>

            <span className={meta.className}>
              CONF · {event.confidence || "—"}
            </span>
          </div>
        </div>

        {/* Description */}
        <p
          data-testid={`timeline-event-desc-${index}`}
          className="mt-3 text-[#e8e8e8] text-[15px] leading-relaxed"
        >
          {event.description}
        </p>

        {/* Confidence Bar */}
        <div className="mt-4">
          <div className="conf-bar">
            <span
              style={{
                width: `${meta.percent}%`,
                background: `linear-gradient(90deg, ${meta.color}, ${meta.color}88)`,
              }}
            />
          </div>

          <div className="flex items-center justify-between mt-1">
            <span className="font-mono text-[10px] text-[#6b7280]">
              EVIDENCE WEIGHT
            </span>
            <span className="font-mono text-[10px] text-[#e3cb96]">
              {meta.percent}%
            </span>
          </div>
        </div>

        {/* Reasoning */}
        {event.reasoning && (
          <div className="mt-4 border-t border-dashed border-[#23233f] pt-3">
            <button
              data-testid={`timeline-reasoning-toggle-${index}`}
              onClick={() => setIsOpen((prev) => !prev)}
              className="font-stencil text-[11px] text-[#c8a96e] hover:text-[#e3cb96] flex items-center gap-2"
            >
              <svg
                width="10"
                height="10"
                viewBox="0 0 10 10"
                style={{
                  transform: isOpen ? "rotate(90deg)" : "rotate(0)",
                  transition: "transform .2s",
                }}
              >
                <path d="M2 1 L8 5 L2 9 Z" fill="#c8a96e" />
              </svg>

              {isOpen ? "HIDE REASONING" : "SHOW REASONING"}
            </button>

            {isOpen && (
              <p className="mt-2 font-mono text-[12.5px] text-[#a1a7b3] leading-relaxed">
                <span className="text-[#f6b84b]">//</span>{" "}
                {event.reasoning}
              </p>
            )}
          </div>
        )}
      </article>
    </div>
  );
}

/* ------------------ Timeline ------------------ */
export default function Timeline({ events = [] }) {
  if (!events?.length) return null;

  return (
    <section data-testid="timeline-section" className="section">
      {/* Header */}
      <div className="section-title fade-up">
        <span className="bar" />
        <h2 className="section-label text-[15px]">
          // Reconstructed Event Timeline
        </h2>
      </div>

      {/* Timeline */}
      <div className="relative pl-2">
        <div className="timeline-rail" />

        {events.map((event, index) => (
          <EventCard
            key={`${event.step || index}-${index}`}
            event={event}
            index={index}
          />
        ))}
      </div>

      {/* Legend */}
      <div className="mt-4 flex items-center gap-5 text-xs font-mono text-[#6b7280] pl-14">
        <span className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-full border-2 border-[#4fc3f7] bg-[#4fc3f730]" />
          STATED — explicit in FIR
        </span>

        <span className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-full border-2 border-dashed border-[#f6b84b]" />
          INFERRED — AI deduction
        </span>
      </div>
    </section>
  );
}