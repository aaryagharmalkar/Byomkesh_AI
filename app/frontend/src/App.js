import React, { useEffect, useState } from "react";
import axios from "axios";
import { Toaster, toast } from "sonner";
import "@/App.css";

import TopNav from "@/components/TopNav";
import Hero from "@/components/Hero";
import UploadModule from "@/components/UploadModule";
import Processing from "@/components/Processing";
import EvidencePanel from "@/components/EvidencePanel";
import Timeline from "@/components/Timeline";
import AlternateScenarios from "@/components/AlternateScenarios";
import CaseSummary from "@/components/CaseSummary";
import Footer from "@/components/Footer";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "http://127.0.0.1:8000";
const API = `${BACKEND_URL}/api`;

export default function App() {
  const [analysis, setAnalysis] = useState(null);
  const [busy, setBusy] = useState(false);

  // Smooth scroll helpers
  const scrollTo = (id) => {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  const handleLoadDemo = async () => {
    try {
      const res = await axios.get(`${API}/demo/fir`);
      const textarea = document.querySelector('[data-testid="fir-textarea"]');
      if (textarea) {
        const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set;
        setter.call(textarea, res.data.fir_text);
        textarea.dispatchEvent(new Event("input", { bubbles: true }));
        textarea.focus();
      }
      toast.success("Demo FIR loaded — Palakkad burglary (2024-03-14)");
    } catch (e) {
      toast.error("Could not reach /api/demo/fir");
    }
  };

  const handleAnalyze = async (firText) => {
    setBusy(true);
    setAnalysis(null);
    // Scroll into processing zone
    setTimeout(() => scrollTo("processing"), 200);
    try {
      const res = await axios.post(`${API}/cases/analyze`, {
        fir_text: firText,
        officer: "INSP. SHARMA",
      });
      setAnalysis(res.data);
      toast.success(`Reconstruction complete · ${res.data.case_id}`);
      setTimeout(() => scrollTo("timeline-anchor"), 300);
    } catch (e) {
      const msg = e?.response?.data?.detail || e.message || "Analysis failed";
      toast.error(`Reasoning engine error: ${msg}`);
    } finally {
      setBusy(false);
    }
  };

  // Keyboard shortcut: Cmd/Ctrl+K to focus textarea
  useEffect(() => {
    const onKey = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        scrollTo("intake");
        const ta = document.querySelector('[data-testid="fir-textarea"]');
        ta?.focus();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const caseId = analysis?.case_id || "CASE #2024-MH-4471";

  return (
    <div className="app-shell" data-testid="app-root">
      <Toaster
        theme="dark"
        position="top-right"
        toastOptions={{
          style: {
            background: "#0f0f1a",
            border: "1px solid #1a1a2e",
            color: "#e8e8e8",
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: "12px",
          },
        }}
      />
      <TopNav caseId={caseId} officer={analysis?.officer || "INSP. SHARMA"} />
      <Hero
        onUploadClick={() => scrollTo("intake")}
        onViewCasesClick={() => scrollTo("intake")}
      />
      <UploadModule onSubmit={handleAnalyze} onLoadDemo={handleLoadDemo} busy={busy} />

      {busy && (
        <div id="processing">
          <Processing done={false} />
        </div>
      )}

      {analysis && (
        <>
          <div id="timeline-anchor" />
          <EvidencePanel entities={analysis.entities} />
          <Timeline events={analysis.timeline} />
          <AlternateScenarios scenarios={analysis.alternate_scenarios} />
          <CaseSummary analysis={analysis} />
        </>
      )}

      <Footer caseId={caseId} />
    </div>
  );
}
