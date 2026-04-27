"""
MODULE 2: NLP Extractor

Raw fact extraction from FIR text using spaCy NER + regex rules.
Output: ExtractedFacts object (internal schema, not exposed to frontend)
"""

import logging
import re
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger("byomkesh.nlp")

# Singleton spaCy model to avoid reloading per-request
_NLP_MODEL = None


def _get_spacy_model():
    """Load spaCy model once at startup."""
    global _NLP_MODEL
    if _NLP_MODEL is None:
        try:
            import spacy

            _NLP_MODEL = spacy.load("en_core_web_sm")
            logger.info("[NLP] spaCy model loaded: en_core_web_sm")
        except OSError:
            logger.warning(
                "[NLP] spaCy model not found; regex-only extraction will be used. "
                "Run: python -m spacy download en_core_web_sm"
            )
            _NLP_MODEL = None
    return _NLP_MODEL


@dataclass
class ExtractedFacts:
    """Internal schema for raw fact extraction (not exposed to frontend)."""

    times: list[str] = field(default_factory=list)
    locations: list[str] = field(default_factory=list)
    actors: list[dict] = field(default_factory=list)  # [{"role": "...", "description": "..."}]
    entry_points: list[str] = field(default_factory=list)
    exit_points: list[str] = field(default_factory=list)
    actions: list[str] = field(default_factory=list)
    items: list[str] = field(default_factory=list)
    raw_events: list[str] = field(default_factory=list)
    witness_info: list[dict] = field(default_factory=list)  # [{"name": "...", "observation": "..."}]
    has_time_gap: bool = False
    confidence_base: float = 1.0


class NLPExtractor:
    """Extract structured facts from FIR narrative."""

    def __init__(self):
        self.nlp = _get_spacy_model()
        self.has_spacy = self.nlp is not None

    def extract(self, fir_text: str) -> ExtractedFacts:
        """
        Convert raw FIR text → ExtractedFacts.

        Returns:
            ExtractedFacts object containing extracted facts
        """
        facts = ExtractedFacts()

        # LAYER 1: spaCy NER (if available)
        if self.has_spacy:
            self._extract_spacy(fir_text, facts)

        # LAYER 2: Regex rule-based extraction (always runs)
        self._extract_times(fir_text, facts)
        self._extract_locations(fir_text, facts)
        self._extract_entry_points(fir_text, facts)
        self._extract_exit_points(fir_text, facts)
        self._extract_items(fir_text, facts)
        self._extract_actors(fir_text, facts)
        self._extract_actions(fir_text, facts)
        self._extract_witness_info(fir_text, facts)

        # Confidence adjustment
        self._compute_confidence_base(facts)

        # Log summary
        logger.info(
            f"[NLP] extracted {len(facts.times)} times, {len(facts.locations)} locations, "
            f"{len(facts.actors)} actors, {len(facts.entry_points)} entry_points, "
            f"{len(facts.items)} items, confidence_base={facts.confidence_base:.2f}"
        )

        return facts

    def _extract_spacy(self, text: str, facts: ExtractedFacts):
        """spaCy NER pass: extract entities."""
        if not self.has_spacy:
            return

        try:
            doc = self.nlp(text)

            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    # Try to infer role from context
                    role = self._infer_actor_role(text, ent.text)
                    facts.actors.append({"name": ent.text, "role": role, "description": ent.text})

                elif ent.label_ == "GPE":  # Geopolitical entity (city, country)
                    if ent.text not in facts.locations:
                        facts.locations.append(ent.text)

                elif ent.label_ == "FAC":  # Facility
                    if ent.text not in facts.locations:
                        facts.locations.append(ent.text)

                elif ent.label_ == "DATE":
                    if ent.text not in facts.times:
                        facts.times.append(ent.text)

                elif ent.label_ == "TIME":
                    if ent.text not in facts.times:
                        facts.times.append(ent.text)

        except Exception as e:
            logger.warning(f"[NLP] spaCy processing error: {e}")

    def _extract_times(self, text: str, facts: ExtractedFacts):
        """Extract time mentions via regex."""
        # HH:MM format
        time_patterns = [
            r"\b([0-2]?[0-9]:[0-5][0-9])\s*(hours|hrs?|AM|PM)\b",
            r"\b(midnight|noon|morning|afternoon|evening|night)\b",
            r"\b(around|approximately|at about)\s+([0-2]?[0-9]:[0-5][0-9])",
            r"\b([0-2]?[0-9]:[0-5][0-9])\s*(?:hours|hrs?|a\.m\.|p\.m\.)?",
        ]

        for pattern in time_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    time_str = " ".join([m.strip() for m in match if m.strip()])
                else:
                    time_str = match.strip()
                if time_str and time_str not in facts.times:
                    facts.times.append(time_str)

        facts.has_time_gap = len(facts.times) == 0

    def _extract_locations(self, text: str, facts: ExtractedFacts):
        """Extract location mentions."""
        location_keywords = [
            r"residence\s+(?:at\s+)?([^.,;]+(?:(?:,\s*)?[A-Z][a-z]+)*)",
            r"(?:at|near|from|to)\s+([0-9]+-?[A-Z][a-zA-Z\s]+(?:Nagar|Street|Road|Lane|Palakkad|Mumbai|Delhi)[^.,;]*)",
            r"([A-Z][a-zA-Z\s]*(?:Nagar|Street|Road|Lane|Palakkad|Mumbai|Delhi|Bangalore|Chennai)[^.,;]*)",
            r"(\d+[-/]?[A-Z][a-zA-Z\s]+)",
        ]

        for pattern in location_keywords:
            matches = re.findall(pattern, text)
            for match in matches:
                loc = match.strip()
                if loc and loc not in facts.locations and len(loc) > 3:
                    facts.locations.append(loc)

    def _extract_entry_points(self, text: str, facts: ExtractedFacts):
        """Extract entry point mentions."""
        # Specific patterns for entry points - avoid false positives
        entry_patterns = [
            r"(?:through|via|through\s+the|entered\s+through)\s+(?:the\s+)?(kitchen|bedroom|living|front|back|side)?\s*(window|door)(?:\s+\w+)?",
            r"(kitchen window|bedroom window|front door|back door|side window)",
            r"(?:entry|entrance).*?(?:the\s+)?(\w+(?:\s+\w+)?(?:window|door))",
        ]

        found = set()
        for pattern in entry_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Get the matched groups
                groups = [g for g in match.groups() if g]
                entry = " ".join(groups) if groups else match.group(0)
                entry = entry.strip()
                
                # Skip very short or obviously wrong entries
                if not entry or len(entry) < 4 or "into" in entry.lower():
                    continue
                
                if entry not in found:
                    # Check if it's "forced" or "broken" in context
                    context_start = max(0, match.start() - 50)
                    context_end = min(len(text), match.end() + 50)
                    context = text[context_start:context_end]
                    
                    if re.search(r"(forced|broke|breaking|broken|smashed|break)", context, re.IGNORECASE):
                        entry = f"{entry} (forced)"
                    
                    found.add(entry)
                    facts.entry_points.append(entry)

    def _extract_exit_points(self, text: str, facts: ExtractedFacts):
        """Extract exit point mentions."""
        exit_keywords = ["exit", "fled through", "escaped through", "left through", "departed"]

        for keyword in exit_keywords:
            pattern = rf"{keyword}\s+(?:the\s+)?(?:through\s+)?(?:the\s+)?(\w+(?:\s+\w+)?)"
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                exit_point = match.strip()
                if exit_point and exit_point not in facts.exit_points:
                    facts.exit_points.append(exit_point)

    def _extract_items(self, text: str, facts: ExtractedFacts):
        """Extract stolen/mentioned items."""
        item_keywords = [
            r"(gold\s+chain|gold\s+necklace|gold\s+ring|gold\s+bracelet)",
            r"(mobile\s+phone|Samsung\s+mobile|iPhone|Android|smartphone)",
            r"(cash|currency|money|coins|rupees)",
            r"(jewellery|jewelry|bracelet|necklace|ring|earring|pendant|watch)",
            r"(laptop|computer|tablet|iPad)",
            r"(bag|purse|wallet|suitcase)",
            r"(Samsung|Apple|Nokia)\s+(\w+)",
        ]

        found = set()
        for pattern in item_keywords:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                item = match.group(0).strip()
                if item and len(item) > 3 and item not in found:
                    # Try to extract quantity if present
                    start_idx = max(0, match.start() - 50)
                    end_idx = min(len(text), match.end() + 50)
                    context = text[start_idx:end_idx]
                    
                    qty_pattern = rf"(?:weighing|of|totaling)?\s*([\d.]+\s*(?:grams?|g|kg|pcs?|pieces?))"
                    qty_match = re.search(qty_pattern, context, re.IGNORECASE)
                    
                    if qty_match:
                        item_with_qty = f"{item} {qty_match.group(1)}"
                        if item_with_qty not in found:
                            facts.items.append(item_with_qty)
                            found.add(item_with_qty)
                    else:
                        facts.items.append(item)
                        found.add(item)

    def _extract_actors(self, text: str, facts: ExtractedFacts):
        """Extract actors (suspect, victim, witness)."""
        actor_patterns = [
            (r"complainant\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)", "victim"),
            (r"(?:Neighbour|Neighbor|Mrs\.|Ms\.|Mr\.)\s+([A-Z][a-zA-Z]+)", "witness"),
            (r"(?:the\s+)?(?:suspect|accused|perpetrator)(?:,\s*)?(?:described as)?\s*(?:a\s+)?(?:male|female)?(?:\s+approximately)?(?:\s+)([^,.;]*?(?:tall|jacket|wearing|dark))", "suspect"),
            (r"([A-Z][a-zA-Z]+)\s+reported", "witness"),
        ]

        found_names = set()
        for pattern, role in actor_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    name = " ".join([m.strip() for m in match if m.strip()])
                else:
                    name = match.strip()
                
                # Clean up name
                name = re.sub(r"\s+", " ", name)  # Collapse spaces
                name = re.sub(r"(tall|wearing|jacket|dark).*", "", name, flags=re.IGNORECASE).strip()
                
                if name and len(name) > 2 and name not in found_names:
                    # Avoid duplicate or junk entries
                    if not any(c.isdigit() for c in name[:1]):  # Don't start with numbers
                        facts.actors.append({"name": name, "role": role, "description": name})
                        found_names.add(name)

    def _extract_actions(self, text: str, facts: ExtractedFacts):
        """Extract action verbs and events."""
        action_keywords = [
            "entered", "gained entry", "broke", "stole", "removed", "fled", "escaped",
            "moved", "moved from", "moved to", "carried", "took", "grabbed",
            "heard", "saw", "observed", "reported", "broke glass"
        ]

        for keyword in action_keywords:
            pattern = rf"\b({keyword})\b"
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                action = match.strip().lower()
                if action not in facts.actions:
                    facts.actions.append(action)

    def _extract_witness_info(self, text: str, facts: ExtractedFacts):
        """Extract witness observations."""
        witness_patterns = [
            r"(?:Neighbour|neighbor|witness)\s+(?:Mrs\.|Ms\.|Mr\.)\s+([A-Z][a-zA-Z\s]+)\s+reported\s+([^.;]*)",
            r"(?:Neighbour|neighbor)\s+reported\s+([^.;]*)",
            r"(?:heard|saw|observed)\s+([^.;]*)",
        ]

        for pattern in witness_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    name, observation = match
                    facts.witness_info.append({
                        "name": name.strip() if name else "Unknown",
                        "observation": observation.strip()
                    })
                else:
                    facts.witness_info.append({
                        "name": "Unknown",
                        "observation": match.strip()
                    })

    def _infer_actor_role(self, text: str, name: str) -> str:
        """Infer role of an actor from context."""
        context_window = 100
        idx = text.find(name)
        if idx == -1:
            return "unknown"

        context = text[max(0, idx - context_window) : min(len(text), idx + context_window)].lower()

        if any(w in context for w in ["suspect", "accused", "perpetrator", "intruder"]):
            return "suspect"
        elif any(w in context for w in ["victim", "complainant", "reported"]):
            return "victim"
        elif any(w in context for w in ["witness", "neighbour", "neighbor", "heard", "saw"]):
            return "witness"

        return "unknown"

    def _compute_confidence_base(self, facts: ExtractedFacts):
        """Compute base confidence from extraction completeness."""
        confidence = 1.0

        if len(facts.times) == 0:
            confidence -= 0.2
            facts.has_time_gap = True
        if len(facts.locations) == 0:
            confidence -= 0.1
        if len(facts.actors) == 0:
            confidence -= 0.15
        if len(facts.entry_points) == 0:
            confidence -= 0.1

        facts.confidence_base = max(0.1, confidence)
