"""
MODULE 3: Reasoning Engine

Rule-based inference layer + LLM assist for gap-filling.

LAYER 1: Deterministic rule engine (always runs)
LAYER 2: LLM assist (calls Groq for scenario filling and gap detection)

Output: ReasoningResult with timeline events + alternate scenarios
"""

import json
import logging
from dataclasses import dataclass, field
from typing import Optional

from .nlp_extractor import ExtractedFacts

logger = logging.getLogger("byomkesh.reasoning")


@dataclass
class ReasoningResult:
    """Output of reasoning engine."""

    rule_events: list[dict] = field(default_factory=list)
    llm_events: list[dict] = field(default_factory=list)
    all_events: list[dict] = field(default_factory=list)
    alternate_scenarios: list[dict] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)
    inconsistencies: list[str] = field(default_factory=list)


class ReasoningEngine:
    """Apply rule-based logic + LLM-assisted inference."""

    def __init__(self, groq_client):
        """
        Args:
            groq_client: Groq client instance for LLM calls
        """
        self.groq_client = groq_client

    def reason(self, fir_text: str, extracted: ExtractedFacts) -> ReasoningResult:
        """
        Execute full reasoning pipeline: rules then LLM.

        Args:
            fir_text: Original FIR narrative
            extracted: ExtractedFacts from Module 2

        Returns:
            ReasoningResult with timeline and scenarios
        """
        result = ReasoningResult()

        # LAYER 1: Rule engine
        self._apply_rules(extracted, result)

        # Log rule engine output
        logger.info(
            f"[RULES] applied rules, produced {len(result.rule_events)} events, "
            f"{len([e for e in result.rule_events if e['source'] == 'inferred'])} inferred"
        )

        # LAYER 2: LLM assist
        self._llm_assist(fir_text, extracted, result)

        # Merge and order all events
        result.all_events = sorted(
            result.rule_events + result.llm_events,
            key=lambda e: (e.get("time") or "", e.get("step") or 999),
        )

        logger.info(
            f"[REASONING] final: {len(result.all_events)} events, "
            f"{len(result.alternate_scenarios)} scenarios, {len(result.gaps)} gaps"
        )

        return result

    def _apply_rules(self, extracted: ExtractedFacts, result: ReasoningResult):
        """LAYER 1: Deterministic rule engine."""

        # Collect all events from rules
        events = []

        # ORDERING RULES: Create stated events
        # R1: Entry point exists
        if extracted.entry_points:
            for entry in extracted.entry_points:
                events.append({
                    "event": f"Entry via {entry}",
                    "time": extracted.times[0] if extracted.times else None,
                    "source": "stated",
                    "confidence": "high",
                    "reason": "Explicitly stated in FIR" if extracted.times else "No time specified"
                })

        # R2: Movement actions
        if any(a in ["moved", "moved from"] for a in extracted.actions):
            events.append({
                "event": "Movement through premises",
                "time": None,
                "source": "stated",
                "confidence": "high",
                "reason": "Movement explicitly described in FIR"
            })

        # R3: Theft/items stolen
        if extracted.items:
            items_str = ", ".join(extracted.items)
            events.append({
                "event": f"Theft of {items_str}",
                "time": None,
                "source": "stated",
                "confidence": "high",
                "reason": "Items explicitly mentioned as stolen/removed"
            })

        # R4: Exit point exists
        if extracted.exit_points:
            for exit_pt in extracted.exit_points:
                events.append({
                    "event": f"Exit via {exit_pt}",
                    "time": None,
                    "source": "stated",
                    "confidence": "high",
                    "reason": "Escape route explicitly stated in FIR"
                })

        # R5: Witness info exists
        if extracted.witness_info:
            for witness in extracted.witness_info:
                events.append({
                    "event": f"Witness observation by {witness.get('name', 'Unknown')}",
                    "time": None,
                    "source": "stated",
                    "confidence": "high",
                    "reason": f"Witness reported: {witness.get('observation', '')[:60]}..."
                })

        # INFERENCE RULES: Create inferred events
        # I1: Transit between entry and crime location
        if extracted.entry_points and extracted.items:
            events.append({
                "event": "Movement through premises to theft location",
                "time": None,
                "source": "inferred",
                "confidence": "medium",
                "reason": "Entry point and theft location differ — transit implied"
            })

        # I2: Prior knowledge of item location
        if extracted.items and len(extracted.entry_points) > 0:
            events.append({
                "event": "Suspect had knowledge of item location",
                "time": None,
                "source": "inferred",
                "confidence": "low",
                "reason": "Direct movement to specific valuable items suggests prior knowledge or reconnaissance"
            })

        # I3: Witness heard approach before stated crime time
        if extracted.witness_info and extracted.times and len(extracted.times) >= 2:
            events.append({
                "event": "Suspect arrived at location before entry",
                "time": extracted.times[-1] if len(extracted.times) > 1 else None,
                "source": "inferred",
                "confidence": "low",
                "reason": "Witness report (glass breaking) precedes stated entry time — earlier arrival inferred"
            })

        # I4: Forced entry suggests reconnaissance
        if any("forced" in str(e).lower() for e in extracted.entry_points):
            events.append({
                "event": "Suspect performed prior reconnaissance",
                "time": None,
                "source": "inferred",
                "confidence": "low",
                "reason": "Forced entry through specific point suggests prior location survey"
            })

        # I5 & I6: Gap detection
        if not any(a.get("role") == "suspect" for a in extracted.actors):
            result.gaps.append("No suspect description available — identification incomplete")

        if extracted.has_time_gap:
            result.gaps.append("Timeline is incomplete — several events lack specific timestamps")

        result.rule_events = events

    def _llm_assist(self, fir_text: str, extracted: ExtractedFacts, result: ReasoningResult):
        """
        LAYER 2: LLM-assisted gap filling.

        Call Groq with a focused prompt to:
        1. Identify missing events
        2. Suggest alternate scenarios
        3. Flag inconsistencies
        """

        # Build LLM prompt
        rule_events_str = "\n".join([
            f"  - {e['event']} ({e['source']}, {e['confidence']})"
            for e in result.rule_events
        ])

        facts_str = f"""
Facts extracted:
- Times: {', '.join(extracted.times) if extracted.times else 'None specified'}
- Locations: {', '.join(extracted.locations) if extracted.locations else 'None'}
- Actors: {', '.join(f"{a['name']} ({a['role']})" for a in extracted.actors) if extracted.actors else 'None'}
- Entry points: {', '.join(extracted.entry_points) if extracted.entry_points else 'None'}
- Exit points: {', '.join(extracted.exit_points) if extracted.exit_points else 'None'}
- Items: {', '.join(extracted.items) if extracted.items else 'None'}
- Witness info: {len(extracted.witness_info)} witnesses
"""

        prompt = f"""You are a forensic reasoning assistant. You are given:

1. A raw FIR narrative
2. Facts extracted from it
3. A partial timeline already built by a rule engine

Your job is ONLY to:
1. Identify any MISSING events that are logically implied but not captured
2. Suggest 1-2 alternate scenarios with probability estimates
3. Flag any inconsistencies between facts

STRICT RULES:
- Do NOT repeat events already in the timeline
- Do NOT contradict stated facts
- Mark ALL your additions as source: "inferred"
- Be conservative — only infer what is logically necessary
- Return ONLY valid JSON, no explanation text

FIR Narrative:
{fir_text}

{facts_str}

Timeline already built (rule engine):
{rule_events_str}

Return this exact JSON structure:
{{
"additional_events": [
{{
"event": "...",
"time": "...",
"source": "inferred",
"confidence": "low|medium|high",
"reason": "..."
}}
],
"alternate_scenarios": [
{{
"description": "...",
"probability": 25
}}
],
"inconsistencies": ["..."]
}}"""

        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a forensic AI reasoning assistant. Return only valid JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000,
            )

            llm_text = response.choices[0].message.content or ""

            # Parse JSON response
            try:
                # Try to extract JSON from response
                import re
                json_match = re.search(r"\{.*\}", llm_text, re.DOTALL)
                if json_match:
                    llm_json = json.loads(json_match.group(0))
                else:
                    llm_json = json.loads(llm_text)

                # Process additional events
                for event in llm_json.get("additional_events", []):
                    # Validate: not already in timeline, not contradicting facts
                    if self._validate_event(event, result.rule_events, extracted):
                        result.llm_events.append(event)

                # Process alternate scenarios
                for scenario in llm_json.get("alternate_scenarios", []):
                    if self._validate_scenario(scenario):
                        result.alternate_scenarios.append(scenario)

                # Collect inconsistencies
                result.inconsistencies.extend(llm_json.get("inconsistencies", []))

                logger.info(
                    f"[LLM] added {len(result.llm_events)} events, "
                    f"{len(result.alternate_scenarios)} scenarios"
                )

            except json.JSONDecodeError as e:
                logger.warning(f"[LLM] JSON parse error: {e}; discarding LLM output")

        except Exception as e:
            logger.error(f"[LLM] Groq call failed: {e}; using rule engine output only")

    def _validate_event(self, event: dict, rule_events: list[dict], extracted: ExtractedFacts) -> bool:
        """
        Validate LLM event:
        - Not already in timeline
        - Not contradicting stated facts
        - Has required fields
        """
        if not isinstance(event, dict):
            return False

        # Check required fields
        if "event" not in event or "source" not in event:
            return False

        # Don't duplicate
        event_str = event.get("event", "").lower()
        if any(e.get("event", "").lower() == event_str for e in rule_events):
            return False

        # Don't contradict stated facts
        if event.get("source") == "inferred":
            # Check if contradicts any extracted fact
            event_lower = event_str.lower()
            for actor in extracted.actors:
                if actor["role"] == "suspect" and "suspect" in event_lower:
                    # Don't add conflicting suspect info
                    if "not" in event_lower or "denied" in event_lower:
                        return False

        return True

    def _validate_scenario(self, scenario: dict) -> bool:
        """Validate alternate scenario structure."""
        return (
            isinstance(scenario, dict)
            and "description" in scenario
            and "probability" in scenario
            and 0 <= scenario.get("probability", 0) <= 100
        )
