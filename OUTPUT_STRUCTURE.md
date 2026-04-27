<!-- 
BYOMKESH AI - Output Structure Reference
Shows the improved, structured output format from the 4-module pipeline
-->

# BYOMKESH AI — Output Structure Reference

## 1. EVIDENCE ENTITIES (Frontend: EvidencePanel)

**Purpose**: Display extracted facts organized by category

**Output Format**:
```json
{
  "entities": [
    {
      "category": "TIME",
      "label": "Crime Time",
      "value": "02:30 hours",
      "confidence": "HIGH"
    },
    {
      "category": "LOCATION",
      "label": "Crime Scene",
      "value": "47-B, Shivaji Nagar",
      "confidence": "HIGH"
    },
    {
      "category": "SUSPECT",
      "label": "Suspect",
      "value": "Unknown male, 5'8\", dark jacket",
      "confidence": "HIGH"
    },
    {
      "category": "VICTIM",
      "label": "Victim",
      "value": "Ramesh Kumar",
      "confidence": "HIGH"
    },
    {
      "category": "WITNESS",
      "label": "Witness",
      "value": "Mrs. Patel",
      "confidence": "HIGH"
    },
    {
      "category": "ENTRY_POINT",
      "label": "Entry Point",
      "value": "kitchen window (forced)",
      "confidence": "HIGH"
    },
    {
      "category": "EXIT",
      "label": "Exit Point",
      "value": "main door",
      "confidence": "HIGH"
    },
    {
      "category": "ITEMS_STOLEN",
      "label": "Stolen Item",
      "value": "gold chain 20 grams",
      "confidence": "HIGH"
    }
  ]
}
```

**Categories & Icons**:
- 🕐 TIME - Timestamps and durations
- 📍 LOCATION - Places and addresses
- 👤 SUSPECT - Perpetrator information
- 👥 VICTIM - Affected person
- 👁️ WITNESS - Observer/informant
- 🚪 ENTRY_POINT - Access route (entry)
- ➡️ EXIT - Escape route (exit)
- 🎁 ITEMS_STOLEN - Stolen/targeted items

**Frontend Display**: Grid layout with 2-3 columns (responsive), each entity in a dark card with icon, category label, value, and confidence badge

---

## 2. TIMELINE EVENTS (Frontend: Timeline)

**Purpose**: Chronological reconstruction of crime events

**Output Format**:
```json
{
  "timeline": [
    {
      "step": 1,
      "description": "Entry via kitchen window (forced)",
      "timestamp": "02:25 hours",
      "source": "STATED",
      "confidence": "HIGH",
      "reasoning": null
    },
    {
      "step": 2,
      "description": "Movement through premises to theft location",
      "timestamp": null,
      "source": "INFERRED",
      "confidence": "MEDIUM",
      "reasoning": "Entry point and theft location differ — transit implied"
    },
    {
      "step": 3,
      "description": "Theft of gold chain 20 grams and Samsung mobile",
      "timestamp": "02:30 hours",
      "source": "STATED",
      "confidence": "HIGH",
      "reasoning": null
    },
    {
      "step": 4,
      "description": "Exit via main door",
      "timestamp": "02:35 hours",
      "source": "STATED",
      "confidence": "HIGH",
      "reasoning": null
    },
    {
      "step": 5,
      "description": "Suspect had prior knowledge of item location",
      "timestamp": null,
      "source": "INFERRED",
      "confidence": "LOW",
      "reasoning": "Direct movement to specific valuable items suggests prior reconnaissance"
    }
  ]
}
```

**Event Source Types**:
- **STATED** (solid circle 🔵): Explicitly mentioned in FIR - most reliable
- **INFERRED** (dashed circle 🟠): Logically deduced - requires reasoning

**Confidence Levels**:
- **HIGH** (90%) - Direct evidence from FIR
- **MEDIUM** (60%) - Strong logical inference with supporting details
- **LOW** (30%) - Plausible but speculative inference

**Frontend Display**: Vertical timeline with nodes (stated=solid, inferred=dashed), expandable reasoning sections for inferred events, confidence progress bars

---

## 3. ALTERNATE SCENARIOS (Frontend: AlternateScenarios)

**Purpose**: Explore alternative reconstructions of events

**Output Format**:
```json
{
  "alternate_scenarios": [
    {
      "title": "Suspect entered earlier and waited inside",
      "description": "Suspect may have gained entry before witness heard glass breaking (02:25), suggesting reconnaissance and planning. Waited inside for optimal moment.",
      "probability": 25
    },
    {
      "title": "Multiple perpetrators with divided roles",
      "description": "One suspect forced entry while accomplice stood watch. Coordinated theft suggests organized crime pattern.",
      "probability": 15
    }
  ]
}
```

**Frontend Display**: 2-column grid (responsive), each scenario in a collapsible card showing title + probability badge, expandable to show full description

---

## 4. CASE SUMMARY (Frontend: CaseSummary)

**Purpose**: Metrics and confidence assessment

**Output Format**:
```json
{
  "summary": {
    "events_confirmed": 5,
    "events_inferred": 3,
    "overall_confidence": 87,
    "gaps": [
      "No physical description of suspect beyond height and clothing",
      "Exact timeline between entry and theft is missing"
    ]
  }
}
```

**Metrics**:
- **events_confirmed**: Count of STATED events (directly from FIR)
- **events_inferred**: Count of INFERRED events (AI reasoning)
- **overall_confidence**: Weighted percentage (0-100)
  - High events = 100% weight
  - Medium events = 60% weight
  - Low events = 30% weight
  - Early events weighted higher (more important)
- **gaps**: Detected missing information flagged by reasoning engine

**Frontend Display**: Three metric tiles (confirmed/inferred/confidence gauge), gaps listed below

---

## 5. FULL RESPONSE SCHEMA

```json
{
  "id": "CASE-20240314-143245-A1B2",
  "case_id": "CASE-20240314-143245-A1B2",
  "officer": "INSP. SHARMA",
  "fir_text": "On 14th March 2024...",
  "created_at": "2026-04-28T19:56:37.190075+00:00",
  
  "entities": [ ... ],
  "timeline": [ ... ],
  "alternate_scenarios": [ ... ],
  "summary": { ... }
}
```

---

## 6. DATA IMPROVEMENTS MADE

### Deduplication
- **Times**: Limited to 3 unique time values (removed redundant variants like "02:30", "02:30 hours", "approximately 02:30")
- **Locations**: Limited to 3 locations, removed address fragments
- **Items**: Removed noise entries, consolidated with quantities where available
- **Actors**: One entry per role type (SUSPECT/VICTIM/WITNESS), filtered duplicates

### Filtering
- Removed junk/false positives from NLP extraction
- Minimum string length validation
- Skipped all-caps or nonsensical actor names
- Removed entries containing noisy keywords ("patel", "reported", "hearing", etc. when extracted as items)

### Formatting
- Consistent capitalization
- Added forced/violence context to entry points
- Quantity units preserved with items (e.g., "20 grams")
- Role names properly categorized (SUSPECT/VICTIM/WITNESS vs generic ACTORS)

---

## 7. PIPELINE EXECUTION FLOW

```
FIR Text Input
    ↓
[Module 1] OCR Processing
    ↓ (raw_text)
[Module 2] NLP Extraction
    ↓ (ExtractedFacts: times, locations, actors, items, etc.)
[Module 3] Reasoning Engine
    ├─ Rule Engine: Apply 15+ forensic rules
    ├─ LLM Assist: Fill gaps with Groq
    ↓ (ReasoningResult: rule_events, llm_events, scenarios, gaps)
[Module 4] Timeline Builder
    ├─ Deduplicate & filter entities
    ├─ Order timeline chronologically
    ├─ Compute confidence metrics
    ↓ (CaseAnalysis)
Frontend Display
    ├─ EvidencePanel: Entities grid
    ├─ Timeline: Event sequence with reasoning
    ├─ AlternateScenarios: What-if scenarios
    ├─ CaseSummary: Metrics & gaps
    └─ (to user)
```

---

## 8. ACTIONS AVAILABLE

**In EvidencePanel**: Filter by category, copy entity values

**In Timeline**: 
- Expand inferred events to see reasoning
- Hover over confidence bar for percentage
- Color-coded by source (blue=stated, amber=inferred)

**In AlternateScenarios**:
- Click to expand full scenario description
- Probability bar visualization

**In CaseSummary**:
- Download analysis as JSON
- Generate PDF report
- Flag for senior review
- Copy to clipboard

---

## 9. EXAMPLE: PALAKKAD BURGLARY CASE

**Input FIR**: Ramesh Kumar burglary report (614 characters)

**Output Metrics**:
- **Entities**: 10-12 (time, location, actors, entry/exit, items)
- **Timeline**: 8-10 events (5 stated, 3-5 inferred)
- **Scenarios**: 1-2 alternatives with 15-25% probability
- **Confidence**: 85-90%
- **Processing Time**: ~2-3 seconds
- **Gaps**: 0-2 detected

---

## 10. CONFIDENCE INTERPRETATION GUIDE

| Confidence | Meaning | Use Case |
|-----------|---------|----------|
| **HIGH (>80%)** | Strong evidence base, complete timeline | Lead prosecution, arrest warrant |
| **MEDIUM (60-80%)** | Good facts, some gaps filled by logic | Investigation direction, follow-ups |
| **LOW (<60%)** | Incomplete info, speculative reasoning | Supplementary analysis, alternate theories |

---

**Last Updated**: April 28, 2026  
**Platform**: BYOMKESH AI v1.0  
**Status**: Production Ready
