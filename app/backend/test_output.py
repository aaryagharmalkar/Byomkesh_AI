#!/usr/bin/env python
"""Test script to demonstrate BYOMKESH AI output structure"""

import sys
import json
from modules import NLPExtractor, TimelineBuilder, ReasoningEngine

# Mock groq for testing
class MockGroqClient:
    class Completions:
        def create(self, **kwargs):
            class Response:
                class Choice:
                    class Message:
                        content = json.dumps({
                            'additional_events': [],
                            'alternate_scenarios': [{'description': 'Suspect may have arrived earlier', 'probability': 20}],
                            'inconsistencies': []
                        })
                    message = Message()
                choices = [Choice()]
            return Response()
    completions = Completions()

fir = """On 14th March 2024 at approximately 02:30 hours, complainant Ramesh Kumar reported that unknown persons gained entry into his residence at 47-B, Shivaji Nagar through the kitchen window. The suspect removed a gold chain 20 grams and Samsung mobile phone. The suspect fled through the main door. Mrs. Patel heard glass breaking at 02:25 hours."""

print("TESTING BYOMKESH AI PIPELINE")
print("=" * 75)

# Extract
print("\n[Step 1] Extracting entities from FIR...")
extractor = NLPExtractor()
extracted = extractor.extract(fir)

# Reason
print("[Step 2] Reasoning about events and gaps...")
engine = ReasoningEngine(groq_client=MockGroqClient())
reasoning = engine.reason(fir, extracted)

# Build
print("[Step 3] Building timeline and deduplicating entities...\n")
builder = TimelineBuilder()
analysis = builder.build(fir, extracted, reasoning, 'CASE-TEST-001', 'INSP. SHARMA')

print("CLEANED ENTITIES (Deduplicated):\n")
print(f"{'Category':<15} | {'Value':<45} | Confidence")
print("-" * 75)
for e in analysis['entities']:
    val = e['value'][:43] + '..' if len(e['value']) > 45 else e['value']
    print(f"{e['category']:<15} | {val:<45} | {e['confidence']}")

print(f"\nTIMELINE EVENTS:")
for event in analysis['timeline'][:6]:
    print(f"  Step {event['step']}: {event['description'][:50]}... [{event['source']}]")

print(f"\nSUMMARY METRICS:")
print(f"  Confirmed Events: {analysis['summary']['events_confirmed']}")
print(f"  Inferred Events: {analysis['summary']['events_inferred']}")
print(f"  Overall Confidence: {analysis['summary']['overall_confidence']}%")
print(f"  Total Entities: {len(analysis['entities'])}")
print(f"  Total Timeline Events: {len(analysis['timeline'])}")

print(f"\nGAPS DETECTED:")
for gap in analysis['summary']['gaps'][:2]:
    print(f"  - {gap}")

print("\n" + "=" * 75)
print("SUCCESS: Pipeline working with structured output")
print("Status: BYOMKESH AI ready for frontend integration")
