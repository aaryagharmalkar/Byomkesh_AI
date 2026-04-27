#!/usr/bin/env python
"""
Quick test of the 4-module pipeline with demo FIR.
"""

import sys
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

# Mock Groq client for testing
class MockGroqClient:
    class Completions:
        def create(self, **kwargs):
            class Response:
                class Choice:
                    class Message:
                        content = json.dumps({
                            "additional_events": [
                                {
                                    "event": "Suspect case escape planning",
                                    "time": None,
                                    "source": "inferred",
                                    "confidence": "low",
                                    "reason": "Forced entry and specific item targeting suggest planning"
                                }
                            ],
                            "alternate_scenarios": [
                                {
                                    "description": "Suspect may have entered earlier and waited inside premises before the reported time.",
                                    "probability": 20
                                }
                            ],
                            "inconsistencies": []
                        })
                    
                    message = Message()
                
                choices = [Choice()]
            
            return Response()
    
    completions = Completions()

from modules import OCRModule, NLPExtractor, ReasoningEngine, TimelineBuilder

DEMO_FIR = """On 14th March 2024 at approximately 02:30 hours, complainant Ramesh Kumar reported that unknown persons gained entry into his residence at 47-B, Shivaji Nagar, Palakkad through the kitchen window by breaking the glass pane. The suspect, described as a male approximately 5'8" tall wearing a dark jacket, was seen moving from the kitchen towards the bedroom. The suspect removed a gold chain weighing 20 grams and one Samsung mobile phone from the bedside table. The suspect then fled through the main door in the eastern direction. Neighbour Mrs. Patel reported hearing glass breaking sounds at around 02:25 hours."""

def test_pipeline():
    """Test the 4-module pipeline with demo FIR."""
    print("\n" + "="*70)
    print("TESTING 4-MODULE PIPELINE WITH DEMO FIR")
    print("="*70 + "\n")
    
    # Step 1: OCR
    print("[1/4] OCR Module...")
    ocr = OCRModule()
    raw_text, ocr_applied = ocr.process(DEMO_FIR, input_type="text")
    print(f"  [OK] OCR applied: {ocr_applied}")
    print(f"  [OK] Text length: {len(raw_text)} chars\n")
    
    # Step 2: NLP Extractor
    print("[2/4] NLP Extractor...")
    extractor = NLPExtractor()
    extracted = extractor.extract(raw_text)
    print(f"  [OK] Times: {extracted.times}")
    print(f"  [OK] Locations: {extracted.locations}")
    print(f"  [OK] Actors: {len(extracted.actors)} => {[a['name'] for a in extracted.actors]}")
    print(f"  [OK] Entry points: {extracted.entry_points}")
    print(f"  [OK] Exit points: {extracted.exit_points}")
    print(f"  [OK] Items: {extracted.items}")
    print(f"  [OK] Confidence base: {extracted.confidence_base:.2f}\n")
    
    # Step 3: Reasoning Engine
    print("[3/4] Reasoning Engine...")
    groq_client = MockGroqClient()
    engine = ReasoningEngine(groq_client=groq_client)
    reasoning = engine.reason(raw_text, extracted)
    print(f"  [OK] Rule events: {len(reasoning.rule_events)}")
    print(f"  [OK] LLM events: {len(reasoning.llm_events)}")
    print(f"  [OK] Total events: {len(reasoning.all_events)}")
    print(f"  [OK] Alternate scenarios: {len(reasoning.alternate_scenarios)}")
    print(f"  [OK] Gaps: {len(reasoning.gaps)}")
    
    print("\n  Rule Events:")
    for e in reasoning.rule_events:
        print(f"    - {e['event'][:50]}... ({e['source']}, {e['confidence']})")
    print()
    
    # Step 4: Timeline Builder
    print("[4/4] Timeline Builder...")
    builder = TimelineBuilder()
    analysis = builder.build(
        fir_text=raw_text,
        extracted=extracted,
        reasoning=reasoning,
        case_id="CASE-DEMO-001",
        officer="INSP. SHARMA"
    )
    print(f"  [OK] Case ID: {analysis['case_id']}")
    print(f"  [OK] Entities: {len(analysis['entities'])}")
    print(f"  [OK] Timeline events: {len(analysis['timeline'])}")
    print(f"  [OK] Alternate scenarios: {len(analysis['alternate_scenarios'])}")
    print(f"  [OK] Summary:")
    print(f"      - Events confirmed: {analysis['summary']['events_confirmed']}")
    print(f"      - Events inferred: {analysis['summary']['events_inferred']}")
    print(f"      - Overall confidence: {analysis['summary']['overall_confidence']}%")
    print(f"      - Gaps: {len(analysis['summary']['gaps'])}")
    
    print("\n" + "="*70)
    print("TIMELINE EVENTS:")
    print("="*70)
    for event in analysis['timeline']:
        src_mark = "[STATED]" if event['source'] == 'STATED' else "[INFERRED]"
        print(f"\n{src_mark} STEP {event['step']}: {event['description']}")
        print(f"   Source: {event['source']} | Confidence: {event['confidence']}")
        if event['timestamp']:
            print(f"   Time: {event['timestamp']}")
        if event['reasoning']:
            print(f"   Reasoning: {event['reasoning'][:80]}...")
    
    print("\n" + "="*70)
    print("ENTITIES EXTRACTED:")
    print("="*70)
    for entity in analysis['entities']:
        print(f"  {entity['category']:15} | {entity['value']:40} | {entity['confidence']}")
    
    print("\n" + "="*70)
    print("[OK] PIPELINE TEST COMPLETE")
    print("="*70 + "\n")
    
    return analysis

if __name__ == "__main__":
    analysis = test_pipeline()
    
    # Output full JSON for verification
    print("\nFull Analysis JSON:")
    print(json.dumps(analysis, indent=2, default=str))
