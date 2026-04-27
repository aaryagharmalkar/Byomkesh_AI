import React, { useState } from \"react\";

function confMeta(c) {
  switch ((c || \"\").toUpperCase()) {
    case \"HIGH\":   return { cls: \"badge badge-green\", pct: 90, color: \"#00e676\" };
    case \"MEDIUM\": return { cls: \"badge badge-amber\", pct: 62, color: \"#f6b84b\" };
    case \"LOW\":    return { cls: \"badge badge-red\",   pct: 30, color: \"#e53935\" };
    default:       return { cls: \"badge badge-muted\", pct: 50, color: \"#6b7280\" };
  }
}

function EventCard({ ev, index }) {
  const [open, setOpen] = useState(false);
  const source = (ev.source || \"\").toUpperCase();
  const isStated = source === \"STATED\";
  const meta = confMeta(ev.confidence);
  const stagger = Math.min(6, (index % 6) + 1);

  return (
    <div
      data-testid={`timeline-event-${index}`}
      className=\"relative pl-14 pb-10\"
      style={{ animation: `fade-up 0.7s cubic-bezier(.2,.8,.2,1) both ${0.05 + index * 0.18}s` }}
    >
      {/* Node on rail */}
      <div className=\"absolute left-[9px] top-1\">
        {isStated ? (
          <span
            className=\"block w-[24px] h-[24px] rounded-full border-2 border-[#4fc3f7] bg-[#4fc3f730] pulse-blue\"
            title=\"STATED\"
          />
        ) : (
          <span
            className=\"block w-[24px] h-[24px] rounded-full border-2 border-dashed border-[#f6b84b] bg-transparent pulse-amber\"
            title=\"INFERRED\"
          />
        )}
      </div>

      <article
        className={`card-noir p-5 border-l-2 left-flash stagger-${stagger}`}
        style={{ borderLeftColor: isStated ? \"#4fc3f7\" : \"#f6b84b\" }}
      >
        <div className=\"flex items-center justify-between flex-wrap gap-2\">
          <div className=\"flex items-center gap-3\">
            <span className=\"font-stencil text-[11px] text-[#c8a96e]\">
              STEP {String(ev.step || index + 1).padStart(2, \"0\")}
            </span>
            {ev.timestamp && (
              <span className=\"font-mono text-[12px] text-[#87d6fa]\">
                {ev.timestamp}
              </span>
            )}
          </div>
          <div className=\"flex items-center gap-2\">
            <span className={isStated ? \"badge badge-blue\" : \"badge badge-amber\"}>
              {source || \"—\"}
            </span>
            <span className={meta.cls}>CONF · {ev.confidence || \"—\"}</span>
          </div>
        </div>

        <p data-testid={`timeline-event-desc-${index}`} className=\"mt-3 text-[#e8e8e8] text-[15px] leading-relaxed\">
          {ev.description}
        </p>

        <div className=\"mt-4\">
          <div className=\"conf-bar\">
            <span
              style={{
                width: `${meta.pct}%`,
                background: `linear-gradient(90deg, ${meta.color}, ${meta.color}88)`,
              }}
            />
          </div>
          <div className=\"flex items-center justify-between mt-1\">
            <span className=\"font-mono text-[10px] text-[#6b7280]\">EVIDENCE WEIGHT</span>
            <span className=\"font-mono text-[10px] text-[#e3cb96]\">{meta.pct}%</span>
          </div>
        </div>

        {ev.reasoning && (
          <div className=\"mt-4 border-t border-dashed border-[#23233f] pt-3\">
            <button
              data-testid={`timeline-reasoning-toggle-${index}`}
              onClick={() => setOpen((o) => !o)}
              className=\"font-stencil text-[11px] text-[#c8a96e] hover:text-[#e3cb96] flex items-center gap-2\"
            >
              <svg
                width=\"10\" height=\"10\" viewBox=\"0 0 10 10\"
                style={{ transform: open ? \"rotate(90deg)\" : \"rotate(0)\", transition: \"transform .2s\" }}
              >
                <path d=\"M2 1 L8 5 L2 9 Z\" fill=\"#c8a96e\" />
              </svg>
              {open ? \"HIDE REASONING\" : \"SHOW REASONING\"}
            </button>
            {open && (
              <p className=\"mt-2 font-mono text-[12.5px] text-[#a1a7b3] leading-relaxed\">
                <span className=\"text-[#f6b84b]\">//</span> {ev.reasoning}
              </p>
            )}
          </div>
        )}
      </article>
    </div>
  );
}

export default function Timeline({ events = [] }) {
  if (!events.length) return null;
  return (
    <section data-testid=\"timeline-section\" className=\"section\">
      <div className=\"section-title fade-up\">
        <span className=\"bar\" />
        <h2 className=\"section-label text-[15px]\">// Reconstructed Event Timeline</h2>
      </div>

      <div className=\"relative pl-2\">
        <div className=\"timeline-rail\" />
        {events.map((ev, i) => (
          <EventCard key={i} ev={ev} index={i} />
        ))}
      </div>

      <div className=\"mt-4 flex items-center gap-5 text-xs font-mono text-[#6b7280] pl-14\">
        <span className=\"flex items-center gap-2\">
          <span className=\"w-3 h-3 rounded-full border-2 border-[#4fc3f7] bg-[#4fc3f730]\" />
          STATED — explicit in FIR
        </span>
        <span className=\"flex items-center gap-2\">
          <span className=\"w-3 h-3 rounded-full border-2 border-dashed border-[#f6b84b]\" />
          INFERRED — AI deduction
        </span>
      </div>
    </section>
  );
}
