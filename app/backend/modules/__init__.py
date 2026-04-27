"""
SENTINEL Forensic AI Backend Modules

4-module pipeline:
1. OCR Module: Conditional image text extraction
2. NLP Extractor: Fact extraction via spaCy + regex
3. Reasoning Engine: Rule-based + LLM-assisted inference
4. Timeline Builder: Final CaseAnalysis assembly
"""

from .ocr_module import OCRModule
from .nlp_extractor import NLPExtractor, ExtractedFacts
from .reasoning_engine import ReasoningEngine, ReasoningResult
from .timeline_builder import TimelineBuilder

__all__ = [
    "OCRModule",
    "NLPExtractor",
    "ExtractedFacts",
    "ReasoningEngine",
    "ReasoningResult",
    "TimelineBuilder",
]
