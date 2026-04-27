"# SENTINEL — AI-Driven Crime Scene Reconstruction · PRD

## Original Problem Statement
Full-stack web app for POLICE INVESTIGATORS & FORENSIC ANALYSTS to upload FIR
documents, run AI reasoning on the narrative, and view a reconstructed event
timeline with clear STATED vs INFERRED distinction and confidence levels.
Aesthetic: dark detective noir × futuristic forensic lab (Se7en × Minority Report).

## User Choices (from ask_human)
- React frontend (scaffolded in /app/frontend)
- Minimal FastAPI backend wired to a real reasoning engine
- Real FIR processing with backend (not hardcoded mock)
- \"Extra touches as you wish\"

## Architecture
- **Frontend:** React 19 + CRA + Tailwind (shadcn tokens remapped to noir palette),
  sonner for toasts. Custom SVG shield/eye logo. Google Fonts: Playfair Display,
  JetBrains Mono, Rajdhani.
- **Backend:** FastAPI + Motor (MongoDB). `emergentintegrations.llm.chat.LlmChat`
  bound to `claude-sonnet-4-5-20250929` via `EMERGENT_LLM_KEY`. Structured JSON
  prompt returns entities, timeline events (STATED/INFERRED + HIGH/MEDIUM/LOW +
  reasoning), alternate scenarios, and weighted summary.
- **Persistence:** `cases` collection. `_id` excluded from all responses.

## Core Requirements (static)
- FIR intake: drag-drop + paste textarea + demo-loader
- Reasoning engine produces schema-validated CaseAnalysis
- Timeline is the hero element: vertical rail, stated=solid blue node,
  inferred=dashed amber node, expandable reasoning, animated confidence bar
- Export timeline (JSON), print-ready report, flag for review
- Strictly noir palette (#0a0a0f / #c8a96e / #4fc3f7 / #e53935 / #00e676)

## User Personas
- **Inspector / IO** — primary. Wants fast, explainable reconstructions.
- **Forensic Analyst** — secondary. Needs source-of-evidence transparency
  (STATED vs INFERRED) and confidence weighting.

## Implemented (2026-02)
- [x] Backend: `/api/`, `/api/demo/fir`, `POST /api/cases/analyze`,
      `GET /api/cases`, `GET /api/cases/{case_id}`
- [x] Claude Sonnet 4.5 reasoning with JSON schema prompt
- [x] MongoDB persistence (cases collection)
- [x] Full noir React UI: TopNav (live UTC clock, pulsing ACTIVE CASE, officer
      badge, glitch logo), Hero (typewriter + evidence-board SVG + stat ribbon),
      UploadModule (drag-drop with corner brackets + amber textarea + demo
      loader), Processing (terminal log stagger + forensic ring spinner),
      EvidencePanel (category cards with SVG icons), Timeline (animated rail,
      stated/inferred node styles, left-border flash, confidence bars,
      reasoning toggle), AlternateScenarios, CaseSummary (metric tiles +
      circular SVG gauge + export JSON + print + flag for review), Footer
- [x] Global CSS effects: scanline overlay, dot grid, breathing gradient mesh,
      glitch on logo hover, gold scan-sweep on primary button, pulse rings
- [x] E2E verified by testing agent — 7/7 backend, 11/11 frontend

## Backlog
- **P1** — Real PDF export (currently `window.print()`) via `@react-pdf/renderer`
  or server-side PDF with `weasyprint`
- **P1** — PDF/image OCR for FIR uploads (currently TXT only; other formats
  prompt the user to paste)
- **P2** — Saved-cases browser / history page (`View Active Cases` currently
  scrolls to intake)
- **P2** — Role-based auth (Emergent Google OAuth) and per-officer case scoping
- **P2** — Suspect/actor network graph beside the timeline
- **P3** — Voice dictation of the FIR narrative via OpenAI Whisper
- **P3** — Map view pinning the location entity

## Next Tasks
1. Wire a real Active Cases list page (GET /api/cases → clickable history)
2. Add PDF report generation
3. Add OCR pipeline for scanned FIRs
"