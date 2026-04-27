"import React from \"react\";

const ICONS = {
  TIME: (
    <svg width=\"22\" height=\"22\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" strokeWidth=\"1.5\">
      <circle cx=\"12\" cy=\"12\" r=\"9\" />
      <path d=\"M12 7v5l3 2\" />
    </svg>
  ),
  LOCATION: (
    <svg width=\"22\" height=\"22\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" strokeWidth=\"1.5\">
      <path d=\"M12 21s-7-6.5-7-11a7 7 0 1 1 14 0c0 4.5-7 11-7 11z\" />
      <circle cx=\"12\" cy=\"10\" r=\"2.5\" />
    </svg>
  ),
  ENTRY_POINT: (
    <svg width=\"22\" height=\"22\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" strokeWidth=\"1.5\">
      <path d=\"M3 21h18\" />
      <path d=\"M5 21V7l7-4 7 4v14\" />
      <path d=\"M10 21v-7h4v7\" />
    </svg>
  ),
  ACTORS: (
    <svg width=\"22\" height=\"22\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" strokeWidth=\"1.5\">
      <circle cx=\"9\" cy=\"8\" r=\"3.5\" />
      <path d=\"M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6\" />
      <circle cx=\"17\" cy=\"9\" r=\"2.5\" />
      <path d=\"M21 18c0-2.5-2-4.5-4.5-4.5\" />
    </svg>
  ),
  SUSPECT: (
    <svg width=\"22\" height=\"22\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" strokeWidth=\"1.5\">
      <circle cx=\"12\" cy=\"8\" r=\"3.5\" />
      <path d=\"M4 21c0-4 4-7 8-7s8 3 8 7\" />
      <path d=\"M7 7l10 10\" />
    </svg>
  ),
  VICTIM: (
    <svg width=\"22\" height=\"22\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" strokeWidth=\"1.5\">
      <circle cx=\"12\" cy=\"8\" r=\"3.5\" />
      <path d=\"M4 21c0-4 4-7 8-7s8 3 8 7\" />
    </svg>
  ),
  WITNESS: (
    <svg width=\"22\" height=\"22\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" strokeWidth=\"1.5\">
      <path d=\"M2 12s3-7 10-7 10 7 10 7-3 7-10 7S2 12 2 12z\" />
      <circle cx=\"12\" cy=\"12\" r=\"2.5\" />
    </svg>
  ),
  ITEMS_STOLEN: (
    <svg width=\"22\" height=\"22\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" strokeWidth=\"1.5\">
      <path d=\"M6 7h12l-1.5 13h-9z\" />
      <path d=\"M9 7V5a3 3 0 0 1 6 0v2\" />
      <path d=\"M9 12h6\" />
    </svg>
  ),
  EXIT: (
    <svg width=\"22\" height=\"22\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" strokeWidth=\"1.5\">
      <path d=\"M14 3h5a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-5\" />
      <path d=\"M9 17l5-5-5-5\" />
      <path d=\"M3 12h11\" />
    </svg>
  ),
};

function confClass(c) {
  switch ((c || \"\").toUpperCase()) {
    case \"HIGH\": return \"badge badge-green\";
    case \"MEDIUM\": return \"badge badge-amber\";
    case \"LOW\": return \"badge badge-red\";
    default: return \"badge badge-muted\";
  }
}

function pretty(cat) {
  return (cat || \"\").replace(/_/g, \" \");
}

export default function EvidencePanel({ entities = [] }) {
  if (!entities.length) return null;
  return (
    <section data-testid=\"evidence-panel\" className=\"section\">
      <div className=\"section-title fade-up\">
        <span className=\"bar\" />
        <h2 className=\"section-label text-[15px]\">// Extracted Evidence</h2>
      </div>

      <div className=\"grid-evidence\">
        {entities.map((e, i) => {
          const cat = (e.category || \"\").toUpperCase();
          const icon = ICONS[cat] || ICONS.LOCATION;
          return (
            <article
              key={i}
              data-testid={`evidence-card-${i}`}
              className={`card-noir p-5 fade-up stagger-${Math.min(6, (i % 6) + 1)}`}
            >
              <div className=\"flex items-center justify-between\">
                <span className=\"section-label text-[11px]\">{pretty(cat)}</span>
                <span className=\"text-[#c8a96e]\">{icon}</span>
              </div>
              {e.label && (
                <div className=\"mt-3 font-stencil text-[11px] text-[#6b7280]\">{e.label}</div>
              )}
              <div
                data-testid={`evidence-card-value-${i}`}
                className=\"mt-1 font-display text-[24px] leading-tight text-[#e8e8e8] break-words\"
              >
                {e.value}
              </div>
              <div className=\"mt-4 flex items-center justify-between\">
                <span className={confClass(e.confidence)}>
                  CONF · {e.confidence || \"N/A\"}
                </span>
                <span className=\"font-mono text-[10px] text-[#6b7280]\">#{String(i + 1).padStart(2, \"0\")}</span>
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}
"