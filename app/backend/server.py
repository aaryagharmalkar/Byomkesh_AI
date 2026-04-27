from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import json
import re
import logging
import uuid
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone

from groq import Groq

# Import the 4-module pipeline
from modules import OCRModule, NLPExtractor, ReasoningEngine, TimelineBuilder


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

client = None
db = None
case_store = []

# MongoDB connection
# mongo_url = os.environ['MONGO_URL']
# client = AsyncIOMotorClient(mongo_url)
# db = client[os.environ['DB_NAME']]

GROQ_API_KEY = os.environ.get('GROQ_API_KEY') or os.environ.get('EMERGENT_LLM_KEY')

if not GROQ_API_KEY:
    raise RuntimeError('GROQ_API_KEY is not set')

groq_client = Groq(api_key=GROQ_API_KEY)

app = FastAPI(title="BYOMKESH AI - Forensic Analysis Platform")
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("byomkesh")


# ======================================================================
# Demo FIR (hardcoded as per spec)
# ======================================================================
DEMO_FIR = """On 14th March 2024 at approximately 02:30 hours, complainant Ramesh Kumar reported that unknown persons gained entry into his residence at 47-B, Shivaji Nagar, Palakkad through the kitchen window by breaking the glass pane. The suspect, described as a male approximately 5'8" tall wearing a dark jacket, was seen moving from the kitchen towards the bedroom. The suspect removed a gold chain weighing 20 grams and one Samsung mobile phone from the bedside table. The suspect then fled through the main door in the eastern direction. Neighbour Mrs. Patel reported hearing glass breaking sounds at around 02:25 hours."""


# ======================================================================
# Pydantic models
# ======================================================================
class AnalyzeRequest(BaseModel):
    fir_text: str
    case_id: Optional[str] = None
    officer: Optional[str] = "INSP. SHARMA"


class Entity(BaseModel):
    category: str            # TIME, LOCATION, ENTRY_POINT, ACTORS, ITEMS_STOLEN, EXIT, WITNESS
    label: str
    value: str
    confidence: str = "HIGH"  # HIGH / MEDIUM / LOW


class TimelineEvent(BaseModel):
    step: int
    description: str
    timestamp: Optional[str] = None
    source: str              # STATED or INFERRED
    confidence: str          # HIGH / MEDIUM / LOW
    reasoning: Optional[str] = None


class AlternateScenario(BaseModel):
    title: str
    description: str
    probability: int         # percent 0-100


class CaseSummary(BaseModel):
    events_confirmed: int
    events_inferred: int
    overall_confidence: int  # percent


class CaseAnalysis(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    case_id: str
    officer: str
    fir_text: str
    entities: List[Entity]
    timeline: List[TimelineEvent]
    alternate_scenarios: List[AlternateScenario]
    summary: CaseSummary
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ======================================================================
# LLM prompt & parsing (retained for reference, now handled in modules)
# ======================================================================


def _strip_fences(text: str) -> str:
    """Remove markdown code fences if the model wraps JSON in them."""
    t = text.strip()
    if t.startswith("```"):
        t = re.sub(r"^```(?:json)?\s*", "", t)
        t = re.sub(r"\s*```$", "", t)
    return t.strip()


def _extract_json(text: str) -> dict:
    cleaned = _strip_fences(text)
    # Find first {...} block
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in model response")
    return json.loads(match.group(0))


# ======================================================================
# API routes
# ======================================================================
@api_router.get("/")
async def root():
    return {"service": "SENTINEL", "status": "online"}


@api_router.get("/demo/fir")
async def get_demo_fir():
    return {"fir_text": DEMO_FIR}


@api_router.post("/cases/analyze", response_model=CaseAnalysis)
async def analyze_case(payload: AnalyzeRequest):
    """
    Analyze a FIR narrative using the 4-module pipeline.
    
    Pipeline:
    1. OCR Module: Conditional text extraction
    2. NLP Extractor: Fact extraction via spaCy + regex
    3. Reasoning Engine: Rule-based + LLM-assisted inference
    4. Timeline Builder: Final CaseAnalysis assembly
    """
    
    fir_text = (payload.fir_text or "").strip()
    if len(fir_text) < 40:
        raise HTTPException(status_code=400, detail="FIR narrative is too short to analyse (min 40 chars).")

    case_id = payload.case_id or f"CASE-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:4].upper()}"
    officer = payload.officer or "INSP. SHARMA"

    try:
        # STEP 1: OCR Module (preprocessor)
        logger.info(f"[PIPELINE] Starting analysis for {case_id}")
        ocr = OCRModule()
        raw_text, ocr_applied = ocr.process(fir_text, input_type="text")
        
        # STEP 2: NLP Extractor (fact extraction)
        extractor = NLPExtractor()
        extracted_facts = extractor.extract(raw_text)
        
        # STEP 3: Reasoning Engine (rule + LLM)
        engine = ReasoningEngine(groq_client=groq_client)
        reasoning_result = engine.reason(raw_text, extracted_facts)
        
        # STEP 4: Timeline Builder (final assembly)
        builder = TimelineBuilder()
        analysis_dict = builder.build(
            fir_text=raw_text,
            extracted=extracted_facts,
            reasoning=reasoning_result,
            case_id=case_id,
            officer=officer,
        )
        
        # Convert dict to CaseAnalysis model (validates schema)
        analysis = CaseAnalysis(**analysis_dict)
        
        # Persist to in-memory store
        case_store.append(analysis.model_dump())
        
        logger.info(f"[PIPELINE] Analysis complete for {case_id}")
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"[PIPELINE] Analysis failed for {case_id}")
        raise HTTPException(status_code=502, detail=f"Pipeline processing failed: {str(e)}")


@api_router.get("/cases", response_model=List[CaseAnalysis])
async def list_cases():
    if db is not None:
        docs = await db.cases.find({}, {"_id": 0}).sort("created_at", -1).to_list(200)
    else:
        docs = sorted(case_store, key=lambda item: item["created_at"], reverse=True)
    return docs


@api_router.get("/cases/{case_id}", response_model=CaseAnalysis)
async def get_case(case_id: str):
    if db is not None:
        doc = await db.cases.find_one({"case_id": case_id}, {"_id": 0})
    else:
        doc = next((item for item in case_store if item["case_id"] == case_id), None)
    if not doc:
        raise HTTPException(status_code=404, detail="Case not found")
    return doc


# Mount router
app.include_router(api_router)


def get_cors_origins() -> List[str]:
    raw_origins = os.environ.get(
        'CORS_ORIGINS',
        'http://localhost:3000,http://127.0.0.1:3000',
    )
    origins = [origin.strip() for origin in raw_origins.split(',') if origin.strip()]
    return origins or ['http://localhost:3000', 'http://127.0.0.1:3000']

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("shutdown")
async def shutdown_db_client():
    if client is not None:
        client.close()