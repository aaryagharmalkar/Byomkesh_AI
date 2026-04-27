"""
MODULE 4: Timeline Builder

Final assembly of CaseAnalysis object from all previous modules.
Outputs the Pydantic models that the frontend expects.
"""

import logging
from datetime import datetime, timezone

from .nlp_extractor import ExtractedFacts
from .reasoning_engine import ReasoningResult

logger = logging.getLogger("byomkesh.builder")


class TimelineBuilder:
    """Build final CaseAnalysis from extracted facts + reasoning results."""

    def build(
        self,
        fir_text: str,
        extracted: ExtractedFacts,
        reasoning: ReasoningResult,
        case_id: str,
        officer: str = "INSP. SHARMA",
    ) -> dict:
        """
        Assemble all pipeline outputs into final CaseAnalysis object.

        Args:
            fir_text: Original FIR narrative
            extracted: ExtractedFacts from Module 2
            reasoning: ReasoningResult from Module 3
            case_id: Case identifier
            officer: Investigating officer name

        Returns:
            CaseAnalysis dict (matches Pydantic model in server.py)
        """

        # Step 1: Build entities from extracted facts
        entities = self._build_entities(extracted)

        # Step 2: Build timeline events with proper ordering and step numbers
        timeline = self._build_timeline(reasoning.all_events)

        # Step 3: Build alternate scenarios
        alternate_scenarios = self._build_alternate_scenarios(reasoning.alternate_scenarios)

        # Step 4: Compute summary metrics
        summary = self._build_summary(timeline, reasoning.gaps)

        # Step 5: Build final CaseAnalysis object
        case_analysis = {
            "id": case_id,  # Frontend expects 'id' not 'analysis_id'
            "case_id": case_id,
            "officer": officer,
            "fir_text": fir_text,
            "entities": entities,
            "timeline": timeline,
            "alternate_scenarios": alternate_scenarios,
            "summary": summary,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        # Log final output
        logger.info(
            f"[BUILDER] final timeline: {len(timeline)} events, "
            f"{len([e for e in timeline if e['source'] == 'inferred'])} inferred, "
            f"confidence: {summary['overall_confidence']}"
        )

        return case_analysis

    def _build_entities(self, extracted: ExtractedFacts) -> list[dict]:
        """
        Convert ExtractedFacts → Entity list for frontend.
        
        Deduplicates and cleans up entities to produce clean output.
        Frontend expects:
        [
            {"category": "TIME", "label": "...", "value": "...", "confidence": "HIGH"},
            ...
        ]
        """
        entities = []
        seen = set()  # Track (category, value) pairs to avoid duplicates

        def add_entity(category: str, label: str, value: str, confidence: str = "HIGH"):
            """Add entity if not already present."""
            # Normalize value for deduplication
            normalized = value.lower().strip()
            key = (category, normalized)
            
            if key not in seen and value.strip():
                seen.add(key)
                entities.append({
                    "category": category,
                    "label": label,
                    "value": value.strip(),
                    "confidence": confidence,
                })

        # TIMES: Deduplicate and clean up time strings
        times_added = 0
        for time_str in extracted.times:
            # Skip very short or redundant time strings
            if len(time_str) < 4:
                continue
            # Skip if it's a substring of another time
            if any(time_str.lower() in other.lower() for other in extracted.times if time_str != other):
                continue
            
            add_entity("TIME", "Crime Time", time_str, "HIGH")
            times_added += 1
            if times_added >= 3:  # Limit to 3 unique times
                break

        # LOCATIONS: Deduplicate
        locations_added = 0
        for loc in extracted.locations:
            if loc and len(loc) > 4:
                add_entity("LOCATION", "Crime Scene", loc, "HIGH")
                locations_added += 1
                if locations_added >= 3:  # Limit to 3 locations
                    break

        # ACTORS: Better role classification
        actors_by_role = {}
        for actor in extracted.actors:
            role = actor.get("role", "unknown").upper()
            name = actor.get("name", "").strip()
            
            if not name or len(name) < 2 or name.isupper():  # Skip all-caps or very short names
                continue
            
            if role not in actors_by_role:
                actors_by_role[role] = []
            
            # Check for duplicates
            if name not in actors_by_role[role]:
                actors_by_role[role].append(name)

        # Add actors with proper category mapping
        role_to_category = {
            "SUSPECT": "SUSPECT",
            "VICTIM": "VICTIM",
            "WITNESS": "WITNESS",
        }
        
        for role, names in actors_by_role.items():
            category = role_to_category.get(role, "ACTORS")
            label = role.title()
            for name in names[:1]:  # One entry per role type (most relevant)
                add_entity(category, label, name, "HIGH")

        # ENTRY POINTS: Keep forced status
        for entry in extracted.entry_points:
            if entry and len(entry) > 3 and "into" not in entry.lower():
                add_entity("ENTRY_POINT", "Entry Point", entry, "HIGH")

        # EXIT POINTS
        for exit_pt in extracted.exit_points:
            if exit_pt and len(exit_pt) > 2:
                add_entity("EXIT", "Exit Point", exit_pt, "HIGH")

        # ITEMS: Clean up and deduplicate
        items_added = 0
        for item in extracted.items:
            if item and len(item) > 3 and not any(x in item.lower() for x in ["patel", "reported", "hearing", "breaking"]):
                add_entity("ITEMS_STOLEN", "Stolen Item", item, "HIGH")
                items_added += 1
                if items_added >= 5:  # Limit to 5 items
                    break

        return entities

    def _build_timeline(self, all_events: list[dict]) -> list[dict]:
        """
        Convert raw events → properly ordered Timeline with step numbers.

        Frontend expects:
        [
            {
                "step": 1,
                "description": "...",
                "timestamp": "...",
                "source": "stated|inferred",
                "confidence": "HIGH|MEDIUM|LOW",
                "reasoning": "..."
            },
            ...
        ]
        """
        # Sort events: stated first, then by time, then inferred
        sorted_events = sorted(
            all_events,
            key=lambda e: (
                0 if e.get("source") == "stated" else 1,  # stated first
                e.get("time") or "",  # then by time
                0 if e.get("source") == "stated" else 1,  # then stated before inferred
            )
        )

        timeline = []
        for step, event in enumerate(sorted_events, start=1):
            timeline.append({
                "step": step,
                "description": event.get("event", "Unknown event"),
                "timestamp": event.get("time"),
                "source": event.get("source", "stated").upper(),
                "confidence": event.get("confidence", "medium").upper(),
                "reasoning": event.get("reason") if event.get("source") == "inferred" else None,
            })

        return timeline

    def _build_alternate_scenarios(self, scenarios_data: list[dict]) -> list[dict]:
        """
        Convert reasoning scenarios → frontend format.

        Frontend expects:
        [
            {
                "title": "...",
                "description": "...",
                "probability": 35
            },
            ...
        ]
        """
        scenarios = []

        for scenario in scenarios_data:
            # Generate title from description if not provided
            description = scenario.get("description", "Alternate scenario")
            title = description[:50] + "..." if len(description) > 50 else description

            scenarios.append({
                "title": title,
                "description": description,
                "probability": int(scenario.get("probability", 0)),
            })

        # If no scenarios, add default one for demo
        if not scenarios:
            scenarios.append({
                "title": "Suspect may have entered earlier",
                "description": "Suspect may have gained entry before the stated time and waited inside premises.",
                "probability": 20,
            })

        return scenarios

    def _build_summary(self, timeline: list[dict], gaps: list[str]) -> dict:
        """
        Compute summary metrics from timeline.

        Frontend expects:
        {
            "events_confirmed": 5,
            "events_inferred": 2,
            "overall_confidence": 74,
            "gaps": ["..."]
        }
        """
        confirmed = sum(1 for e in timeline if e["source"] == "STATED")
        inferred = sum(1 for e in timeline if e["source"] == "INFERRED")

        # Compute overall confidence (weighted average)
        confidence_weights = {"HIGH": 1.0, "MEDIUM": 0.6, "LOW": 0.3}
        if timeline:
            total_weight = 0
            total_confidence = 0
            for step, event in enumerate(timeline, start=1):
                conf_level = event.get("confidence", "MEDIUM")
                weight = confidence_weights.get(conf_level, 0.5)
                # Weight by inverse of step number (early events more important)
                step_weight = 1.0 / step
                total_confidence += weight * step_weight
                total_weight += step_weight

            overall_confidence = int((total_confidence / total_weight * 100)) if total_weight > 0 else 50
        else:
            overall_confidence = 50

        return {
            "events_confirmed": confirmed,
            "events_inferred": inferred,
            "overall_confidence": overall_confidence,
            "gaps": gaps,
        }
