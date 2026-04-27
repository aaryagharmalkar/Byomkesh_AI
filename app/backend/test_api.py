#!/usr/bin/env python
"""
Test the backend API endpoint with the new 4-module pipeline.
"""

import requests
import json
import time

# Demo FIR from spec
DEMO_FIR = """On 14th March 2024 at approximately 02:30 hours, complainant Ramesh Kumar reported that unknown persons gained entry into his residence at 47-B, Shivaji Nagar, Palakkad through the kitchen window by breaking the glass pane. The suspect, described as a male approximately 5'8" tall wearing a dark jacket, was seen moving from the kitchen towards the bedroom. The suspect removed a gold chain weighing 20 grams and one Samsung mobile phone from the bedside table. The suspect then fled through the main door in the eastern direction. Neighbour Mrs. Patel reported hearing glass breaking sounds at around 02:25 hours."""

API_URL = "http://127.0.0.1:8000/api"

def test_api():
    """Test the POST /api/cases/analyze endpoint."""
    print("\n" + "="*70)
    print("TESTING BACKEND API WITH 4-MODULE PIPELINE")
    print("="*70 + "\n")
    
    # Test 1: Health check
    print("1. Testing health check endpoint...")
    try:
        response = requests.get(f"{API_URL}/", timeout=5)
        if response.status_code == 200:
            print(f"   [OK] Health check: {response.json()}\n")
        else:
            print(f"   [FAIL] Status: {response.status_code}\n")
            return
    except Exception as e:
        print(f"   [ERROR] Could not reach backend: {e}")
        print("   Make sure backend is running: cd app/backend && uvicorn server:app --reload\n")
        return
    
    # Test 2: Demo FIR endpoint
    print("2. Testing demo FIR endpoint...")
    try:
        response = requests.get(f"{API_URL}/demo/fir", timeout=5)
        if response.status_code == 200:
            fir_data = response.json()
            print(f"   [OK] Demo FIR loaded ({len(fir_data['fir_text'])} chars)\n")
        else:
            print(f"   [FAIL] Status: {response.status_code}\n")
    except Exception as e:
        print(f"   [ERROR] {e}\n")
    
    # Test 3: Analyze FIR with pipeline
    print("3. Testing full pipeline via POST /api/cases/analyze...")
    print(f"   Sending FIR ({len(DEMO_FIR)} chars)...")
    
    try:
        payload = {
            "fir_text": DEMO_FIR,
            "officer": "INSP. SHARMA"
        }
        
        start_time = time.time()
        response = requests.post(f"{API_URL}/cases/analyze", json=payload, timeout=30)
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            analysis = response.json()
            print(f"   [OK] Analysis complete in {elapsed:.2f}s\n")
            
            print("   Analysis Results:")
            print(f"   - Case ID: {analysis['case_id']}")
            print(f"   - Entities: {len(analysis['entities'])}")
            print(f"   - Timeline Events: {len(analysis['timeline'])}")
            print(f"   - Alternate Scenarios: {len(analysis['alternate_scenarios'])}")
            print(f"   - Summary:")
            print(f"     * Events Confirmed: {analysis['summary']['events_confirmed']}")
            print(f"     * Events Inferred: {analysis['summary']['events_inferred']}")
            print(f"     * Overall Confidence: {analysis['summary']['overall_confidence']}%")
            
            print("\n   Timeline Events:")
            for event in analysis['timeline'][:5]:
                src = "[STATED]" if event['source'] == 'STATED' else "[INFERRED]"
                print(f"   {src} {event['description'][:60]}")
            
            if len(analysis['timeline']) > 5:
                print(f"   ... and {len(analysis['timeline']) - 5} more events")
            
            print("\n   [OK] All tests passed!")
            return True
            
        else:
            print(f"   [FAIL] Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}\n")
            return False
            
    except requests.exceptions.Timeout:
        print(f"   [ERROR] Request timeout - backend may be slow or not responding\n")
        return False
    except Exception as e:
        print(f"   [ERROR] {e}\n")
        return False

if __name__ == "__main__":
    success = test_api()
    print("="*70)
    if success:
        print("SUCCESS: Pipeline is working through API!")
    else:
        print("FAILED: Please check backend logs")
    print("="*70 + "\n")
