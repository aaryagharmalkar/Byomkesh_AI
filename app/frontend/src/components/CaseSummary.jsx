"import React from \"react\";
import { toast } from \"sonner\";

function Gauge({ value = 0 }) {
  const v = Math.max(0, Math.min(100, Number(value) || 0));
  const R = 42;
  const C = 2 * Math.PI * R;
  const offset = C - (v / 100) * C;
  const color = v >= 75 ? \"#00e676\" : v >= 50 ? \"#f6b84b\" : \"#e53935\";
  return (
    <svg width=\"112\" height=\"112\" viewBox=\"0 0 100 100\" className=\"block\">
      <circle cx=\"50\" cy=\"50\" r={R} stroke=\"#1a1a2e\" strokeWidth=\"6\" fill=\"none\" />
      <circle
        cx=\"50\" cy=\"50\" r={R}
        stroke={color}
        strokeWidth=\"6\"
        fill=\"none\"
        strokeDasharray={C}
        strokeDashoffset={offset}
        strokeLinecap=\"round\"
        transform=\"rotate(-90 50 50)\"
        style={{ transition: \"stroke-dashoffset 1s ease\" }}
      />
      <text
        x=\"50\" y=\"54\"
        textAnchor=\"middle\"
        fontFamily=\"Playfair Display, serif\"
        fontSize=\"22\"
        fontWeight=\"700\"
        fill=\"#e8e8e8\"
      >
        {v}%
      </text>
    </svg>
  );
}

export default function CaseSummary({ analysis }) {
  if (!analysis) return null;
  const { summary, case_id } = analysis;

  const downloadJSON = () => {
    const blob = new Blob([JSON.stringify(analysis, null, 2)], { type: \"application/json\" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement(\"a\");
    a.href = url;
    a.download = `${case_id}_sentinel.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast.success(\"Timeline exported as JSON\");
  };

  const printReport = () => {
    window.print();
  };

  const flagReview = () => {
    toast(\"Case flagged for senior review.\", {
      description: `${case_id} queued to Central Forensic Bureau`,
      icon: \"⚑\",
    });
  };

  return (
    <section data-testid=\"case-summary\" className=\"section\">
      <div className=\"section-title fade-up\">
        <span className=\"bar\" />
        <h2 className=\"section-label text-[15px]\">// Case Analysis Summary</h2>
      </div>

      <div className=\"grid md:grid-cols-3 gap-4\">
        <div data-testid=\"metric-confirmed\" className=\"metric-tile fade-up stagger-1\">
          <div className=\"section-label text-[11px]\">Events Confirmed</div>
          <div className=\"value mt-2 text-[#87d6fa]\">{summary.events_confirmed}</div>
          <div className=\"font-mono text-[11px] text-[#6b7280] mt-1\">STATED in FIR</div>
          <span className=\"absolute top-3 right-3 dot dot-blue pulse-blue\" />
        </div>
        <div data-testid=\"metric-inferred\" className=\"metric-tile fade-up stagger-2\">
          <div className=\"section-label text-[11px]\">Events Inferred</div>
          <div className=\"value mt-2 text-[#f6b84b]\">{summary.events_inferred}</div>
          <div className=\"font-mono text-[11px] text-[#6b7280] mt-1\">AI-deduced</div>
          <span className=\"absolute top-3 right-3 dot dot-amber pulse-amber\" />
        </div>
        <div data-testid=\"metric-confidence\" className=\"metric-tile fade-up stagger-3 flex items-center gap-5\">
          <Gauge value={summary.overall_confidence} />
          <div>
            <div className=\"section-label text-[11px]\">Overall Confidence</div>
            <div className=\"font-mono text-[11px] text-[#6b7280] mt-2 leading-relaxed max-w-[180px]\">
              Weighted across stated evidence, inferred links & supporting witness claims.
            </div>
          </div>
        </div>
      </div>

      <div className=\"mt-8 flex flex-wrap gap-3 no-print\">
        <button
          data-testid=\"export-json-btn\"
          onClick={downloadJSON}
          className=\"btn-outline-blue px-5 py-2.5 text-[12px] flex items-center gap-2\"
        >
          <svg width=\"14\" height=\"14\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" strokeWidth=\"1.7\">
            <path d=\"M12 3v12\" /><path d=\"M7 10l5 5 5-5\" /><path d=\"M4 21h16\" />
          </svg>
          Export Timeline (JSON)
        </button>
        <button
          data-testid=\"export-pdf-btn\"
          onClick={printReport}
          className=\"btn-gold px-5 py-2.5 text-[12px] flex items-center gap-2\"
        >
          <svg width=\"14\" height=\"14\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" strokeWidth=\"1.7\">
            <path d=\"M6 2h9l5 5v15H6z\" /><path d=\"M14 2v6h6\" /><path d=\"M9 13h6M9 17h6\" />
          </svg>
          Generate Report (PDF)
        </button>
        <button
          data-testid=\"flag-review-btn\"
          onClick={flagReview}
          className=\"px-5 py-2.5 text-[12px] font-stencil tracking-[0.22em] border border-[#e5393566] text-[#ff7a77] hover:bg-[#e5393510]\"
        >
          Flag for Review
        </button>
      </div>
    </section>
  );
}
"