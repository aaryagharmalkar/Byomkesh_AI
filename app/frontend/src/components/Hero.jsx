import React, { useEffect, useState } from \"react\";

/** Types a string character-by-character, then calls onDone. */
function useTypewriter(text, speed = 45, startDelay = 200) {
  const [out, setOut] = useState(\"\");
  const [done, setDone] = useState(false);
  useEffect(() => {
    setOut(\"\");
    setDone(false);
    let i = 0;
    const start = setTimeout(() => {
      const id = setInterval(() => {
        i += 1;
        setOut(text.slice(0, i));
        if (i >= text.length) {
          clearInterval(id);
          setDone(true);
        }
      }, speed);
    }, startDelay);
    return () => clearTimeout(start);
  }, [text, speed, startDelay]);
  return { out, done };
}

export default function Hero({ onUploadClick, onViewCasesClick }) {
  const { out, done } = useTypewriter(\"RECONSTRUCT. REASON. REVEAL.\", 55, 300);

  return (
    <section
      data-testid=\"hero-section\"
      className=\"relative overflow-hidden border-b border-[#1a1a2e]\"
    >
      {/* Evidence board background — strings & pins in SVG */}
      <svg
        className=\"absolute inset-0 w-full h-full opacity-40 pointer-events-none\"
        xmlns=\"http://www.w3.org/2000/svg\"
      >
        <defs>
          <pattern id=\"dots\" width=\"36\" height=\"36\" patternUnits=\"userSpaceOnUse\">
            <circle cx=\"1\" cy=\"1\" r=\"1\" fill=\"rgba(200,169,110,0.18)\" />
          </pattern>
        </defs>
        <rect width=\"100%\" height=\"100%\" fill=\"url(#dots)\" />
        {/* Evidence strings */}
        <line x1=\"5%\" y1=\"20%\" x2=\"70%\" y2=\"80%\" stroke=\"rgba(229,57,53,0.35)\" strokeWidth=\"0.6\" />
        <line x1=\"80%\" y1=\"10%\" x2=\"15%\" y2=\"70%\" stroke=\"rgba(79,195,247,0.25)\" strokeWidth=\"0.5\" />
        <line x1=\"30%\" y1=\"90%\" x2=\"90%\" y2=\"30%\" stroke=\"rgba(200,169,110,0.35)\" strokeWidth=\"0.5\" />
        {/* Pins */}
        <circle cx=\"5%\" cy=\"20%\" r=\"3\" fill=\"#c8a96e\" />
        <circle cx=\"70%\" cy=\"80%\" r=\"3\" fill=\"#c8a96e\" />
        <circle cx=\"80%\" cy=\"10%\" r=\"3\" fill=\"#4fc3f7\" />
        <circle cx=\"15%\" cy=\"70%\" r=\"3\" fill=\"#4fc3f7\" />
        <circle cx=\"30%\" cy=\"90%\" r=\"3\" fill=\"#e53935\" />
        <circle cx=\"90%\" cy=\"30%\" r=\"3\" fill=\"#e53935\" />
      </svg>

      <div className=\"max-w-[1280px] mx-auto px-6 py-24 md:py-32 relative\">
        <div className=\"fade-up stagger-1\">
          <span className=\"section-label\">// Operation Room · Command Center</span>
        </div>

        <h1
          data-testid=\"hero-heading\"
          className={`mt-5 font-display font-bold text-[42px] sm:text-[56px] lg:text-[84px] leading-[0.95] text-[#e8e8e8] ${!done ? \"type-caret\" : \"\"}`}
        >
          {out || \"\u00A0\"}
        </h1>

        <p className=\"mt-6 font-mono text-[#a1a7b3] max-w-[640px] text-sm md:text-base fade-up stagger-3\">
          <span className=\"text-[#c8a96e]\">//</span> AI-Powered Forensic Timeline Reconstruction Engine — trained on thousands of closed cases to surface stated facts, infer missing links, and quantify every conclusion.
        </p>

        <div className=\"mt-10 flex flex-wrap gap-4 fade-up stagger-4\">
          <button
            data-testid=\"hero-upload-btn\"
            onClick={onUploadClick}
            className=\"btn-gold px-7 py-3 text-sm\"
          >
            Upload FIR Document
          </button>
          <button
            data-testid=\"hero-view-cases-btn\"
            onClick={onViewCasesClick}
            className=\"btn-outline-blue px-7 py-3 text-sm\"
          >
            View Active Cases
          </button>
        </div>

        {/* Stat ribbon */}
        <div className=\"mt-14 grid grid-cols-2 md:grid-cols-4 gap-4 fade-up stagger-5\">
          {[
            { k: \"MODEL\", v: \"Claude Sonnet 4.5\" },
            { k: \"CASES RECONSTRUCTED\", v: \"12,847\" },
            { k: \"AVG. CONFIDENCE\", v: \"81.4%\" },
            { k: \"CLASSIFICATION\", v: \"RESTRICTED\" },
          ].map((s) => (
            <div
              key={s.k}
              className=\"border border-[#1a1a2e] bg-[#0f0f1a]/60 px-4 py-3\"
            >
              <div className=\"font-stencil text-[10px] text-[#c8a96e]\">{s.k}</div>
              <div className=\"font-mono text-sm mt-1 text-[#e8e8e8]\">{s.v}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
