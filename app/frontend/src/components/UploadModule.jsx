import React, { useRef, useState } from "react";
import { toast } from "sonner";

/* ------------------ Component ------------------ */
export default function UploadModule({
  onSubmit,
  onLoadDemo,
  busy = false,
}) {
  const [dragOver, setDragOver] = useState(false);
  const [narrative, setNarrative] = useState("");
  const [fileName, setFileName] = useState("");

  const inputRef = useRef(null);

  /* ------------------ File Reader ------------------ */
  const readFile = async (file) => {
    if (!file) return;

    setFileName(file.name);

    try {
      // Placeholder handling (future OCR/PDF)
      if (file.type === "application/pdf") {
        toast.error("PDF parsing not yet wired — paste the FIR narrative.");
        return;
      }

      if (file.type.startsWith("image/")) {
        toast.error("Image OCR not yet wired — paste the FIR narrative.");
        return;
      }

      const content = await file.text();
      setNarrative(content);

      toast.success(`Loaded ${file.name}`);
    } catch (err) {
      console.error(err);
      toast.error("Failed to read file.");
    }
  };

  /* ------------------ Handlers ------------------ */
  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);

    const file = e.dataTransfer.files?.[0];
    readFile(file);
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    const clean = narrative.trim();

    if (clean.length < 40) {
      toast.error("Narrative must be at least 40 characters.");
      return;
    }

    onSubmit?.(clean);
  };

  const handleFileSelect = (e) => {
    const file = e.target.files?.[0];
    readFile(file);
  };

  /* ------------------ UI ------------------ */
  return (
    <section
      id="intake"
      data-testid="upload-module"
      className="section"
    >
      {/* Header */}
      <div className="section-title fade-up">
        <span className="bar" />
        <h2 className="section-label text-[15px]">
          // Evidence Intake
        </h2>
      </div>

      <form
        onSubmit={handleSubmit}
        className="grid lg:grid-cols-5 gap-6"
      >
        {/* Drop Zone */}
        <div
          data-testid="drop-zone"
          onDragOver={(e) => {
            e.preventDefault();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => inputRef.current?.click()}
          className={`evidence-frame ${
            dragOver ? "dragover" : ""
          } lg:col-span-2 cursor-pointer flex flex-col items-center justify-center text-center px-6 py-10 min-h-[320px] fade-up stagger-2`}
          role="button"
          aria-label="Upload FIR document"
        >
          {/* Corners */}
          <span className="corner-tl" />
          <span className="corner-tr" />
          <span className="corner-bl" />
          <span className="corner-br" />

          {/* Hidden Input */}
          <input
            ref={inputRef}
            type="file"
            accept=".txt,.pdf,.png,.jpg,.jpeg"
            className="hidden"
            onChange={handleFileSelect}
            data-testid="file-input"
          />

          {/* Icon */}
          <svg
            width="44"
            height="44"
            viewBox="0 0 24 24"
            fill="none"
            stroke="#c8a96e"
            strokeWidth="1.5"
          >
            <path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z" />
            <path d="M14 3v6h6" />
            <circle cx="11" cy="14" r="2.5" />
            <path d="M13 16l2 2" />
          </svg>

          {/* Text */}
          <div className="mt-4 font-stencil text-[#e3cb96] tracking-[0.3em] text-sm">
            Drop FIR Document Here
          </div>

          <div className="mt-2 font-mono text-xs text-[#6b7280]">
            Accepts: PDF · JPG · PNG · TXT
          </div>

          {/* File Name */}
          {fileName && (
            <div className="mt-4 font-mono text-[11px] text-[#4fc3f7]">
              {fileName}
            </div>
          )}

          <div className="mt-5 font-mono text-[10px] text-[#6b7280]">
            CLICK TO BROWSE · OR DRAG-AND-DROP
          </div>
        </div>

        {/* Text Area */}
        <div className="lg:col-span-3 flex flex-col gap-3 fade-up stagger-3">
          <div className="flex items-center justify-between">
            <span className="section-label">
              // Paste FIR Narrative
            </span>

            <button
              type="button"
              onClick={onLoadDemo}
              data-testid="load-demo-btn"
              className="font-stencil text-[11px] text-[#4fc3f7] hover:text-[#7ed3fa] border border-[#4fc3f766] px-3 py-1"
            >
              Load Demo FIR
            </button>
          </div>

          <textarea
            data-testid="fir-textarea"
            value={narrative}
            onChange={(e) => setNarrative(e.target.value)}
            placeholder="// Paste FIR narrative: time, location, suspects, witnesses, items, entry/exit..."
            className="w-full min-h-[260px] bg-[#05050a] border border-[#1a1a2e] focus:border-[#c8a96e] outline-none p-4 font-mono text-sm text-[#f6b84b] caret-[#c8a96e] leading-relaxed resize-vertical"
          />

          {/* Footer */}
          <div className="flex items-center justify-between">
            <span className="font-mono text-[11px] text-[#6b7280]">
              {narrative.length} characters
            </span>

            <button
              type="submit"
              disabled={busy}
              data-testid="initiate-analysis-btn"
              className={`btn-gold px-8 py-3 text-[13px] ${
                busy ? "opacity-70 cursor-wait scanning" : ""
              }`}
            >
              {busy ? "Analysing…" : "Initiate Analysis"}
            </button>
          </div>
        </div>
      </form>
    </section>
  );
}