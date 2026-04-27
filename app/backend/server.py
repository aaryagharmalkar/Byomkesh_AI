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

from emergentintegrations.llm.chat import LlmChat, UserMessage


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

EMERGENT_LLM_KEY = os.environ['EMERGENT_LLM_KEY']

app = FastAPI(title=\"SENTINEL Forensic AI\")
api_router = APIRouter(prefix=\"/api\")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(\"sentinel\")


# ======================================================================
# Demo FIR (hardcoded as per spec)
# ======================================================================
DEMO_FIR = (
    \"On 14th March 2024 at approximately 02:30 hours, complainant Ramesh Kumar \"
    \"reported that unknown persons gained entry into his residence at \"
    \"47-B, Shivaji Nagar, Palakkad through the kitchen window by breaking \"
    \"the glass pane. The suspect, described as a male approximately 5'8\\" tall \"
    \"wearing a dark jacket, was seen moving from the kitchen towards the bedroom. \"
    \"The suspect removed a gold chain weighing 20 grams and one Samsung mobile \"
    \"phone from the bedside table. The suspect then fled through the main door \"
    \"in the eastern direction. Neighbour Mrs. Patel reported hearing glass \"
    \"breaking sounds at around 02:25 hours.\"
)


# ======================================================================
# Pydantic models
# ======================================================================
class AnalyzeRequest(BaseModel):
    fir_text: str
    case_id: Optional[str] = None
    officer: Optional[str] = \"INSP. SHARMA\"


class Entity(BaseModel):
    category: str            # TIME, LOCATION, ENTRY_POINT, ACTORS, ITEMS_STOLEN, EXIT, WITNESS
    label: str
    value: str
    confidence: str = \"HIGH\"  # HIGH / MEDIUM / LOW


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
# LLM prompt & parsing
# ======================================================================
SYSTEM_PROMPT = \"\"\"You are SENTINEL, a forensic AI reasoning engine used by police investigators to reconstruct crime scenes from First Information Reports (FIRs).

Your job: read an FIR narrative and produce a structured, forensically-rigorous reconstruction.

You MUST distinguish between:
- STATED events: explicitly mentioned in the FIR
- INFERRED events: logically deduced but not explicitly stated (you must justify with \"reasoning\")

Confidence levels:
- HIGH: direct evidence from the narrative
- MEDIUM: strong logical inference with supporting detail
- LOW: plausible but speculative inference

Return ONLY a valid JSON object with this EXACT schema, no preamble, no markdown fences:

{
  \"entities\": [
    {\"category\": \"TIME|LOCATION|ENTRY_POINT|ACTORS|ITEMS_STOLEN|EXIT|WITNESS|VICTIM|SUSPECT\", \"label\": \"short label\", \"value\": \"concise value\", \"confidence\": \"HIGH|MEDIUM|LOW\"}
  ],
  \"timeline\": [
    {\"step\": 1, \"description\": \"what happened\", \"timestamp\": \"HH:MM HRS or null\", \"source\": \"STATED|INFERRED\", \"confidence\": \"HIGH|MEDIUM|LOW\", \"reasoning\": \"why (required for INFERRED, optional for STATED)\"}
  ],
  \"alternate_scenarios\": [
    {\"title\": \"short title\", \"description\": \"alternate possible reconstruction\", \"probability\": 22}
  ],
  \"summary\": {
    \"events_confirmed\": 4,
    \"events_inferred\": 3,
    \"overall_confidence\": 78
  }
}

Rules:
- Provide 5-9 timeline events ordered chronologically
- Every INFERRED event MUST have a reasoning field
- Provide 1-3 alternate scenarios
- probability is an integer percentage 0-100
- overall_confidence is computed weighted across events
- Be terse, precise, forensic in tone
\"\"\"


def _strip_fences(text: str) -> str:
    \"\"\"Remove markdown code fences if the model wraps JSON in them.\"\"\"
    t = text.strip()
    if t.startswith(\"```\"):
        t = re.sub(r\"^```(?:json)?\s*\", \"\", t)
        t = re.sub(r\"\s*```$\", \"\", t)
    return t.strip()


def _extract_json(text: str) -> dict:
    cleaned = _strip_fences(text)
    # Find first {...} block
    match = re.search(r\"\{.*\}\", cleaned, re.DOTALL)
    if not match:
        raise ValueError(\"No JSON object found in model response\")
    return json.loads(match.group(0))


async def analyze_fir_with_llm(fir_text: str, session_id: str) -> dict:
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=session_id,
        system_message=SYSTEM_PROMPT,
    ).with_model(\"anthropic\", \"claude-sonnet-4-5-20250929\")

    user_msg = UserMessage(
        text=f\"Analyse the following FIR narrative and return the JSON reconstruction:

---FIR BEGIN---
{fir_text}
---FIR END---\"
    )
    raw = await chat.send_message(user_msg)
    logger.info(f\"LLM raw length: {len(raw)}\")
    data = _extract_json(raw)
    return data


# ======================================================================
# API routes
# ======================================================================
@api_router.get(\"/\")
async def root():
    return {\"service\": \"SENTINEL\", \"status\": \"online\"}


@api_router.get(\"/demo/fir\")
async def get_demo_fir():
    return {\"fir_text\": DEMO_FIR}


@api_router.post(\"/cases/analyze\", response_model=CaseAnalysis)
async def analyze_case(payload: AnalyzeRequest):
    fir_text = (payload.fir_text or \"\").strip()
    if len(fir_text) < 40:
        raise HTTPException(status_code=400, detail=\"FIR narrative is too short to analyse (min 40 chars).\")

    case_id = payload.case_id or f\"CASE-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:4].upper()}\"
    session_id = f\"sentinel-{case_id}\"

    try:
        data = await analyze_fir_with_llm(fir_text, session_id)
    except Exception as e:
        logger.exception(\"LLM analysis failed\")
        raise HTTPException(status_code=502, detail=f\"Reasoning engine failure: {e}\")

    # Build model (pydantic will validate)
    try:
        analysis = CaseAnalysis(
            case_id=case_id,
            officer=payload.officer or \"INSP. SHARMA\",
            fir_text=fir_text,
            entities=[Entity(**e) for e in data.get(\"entities\", [])],
            timeline=[TimelineEvent(**t) for t in data.get(\"timeline\", [])],
            alternate_scenarios=[AlternateScenario(**a) for a in data.get(\"alternate_scenarios\", [])],
            summary=CaseSummary(**data.get(\"summary\", {
                \"events_confirmed\": 0, \"events_inferred\": 0, \"overall_confidence\": 0
            })),
        )
    except Exception as e:
        logger.exception(\"Schema validation failed\")
        raise HTTPException(status_code=502, detail=f\"Malformed reasoning output: {e}\")

    # Persist
    doc = analysis.model_dump()
    await db.cases.insert_one(doc)
    # Strip Mongo-added _id before returning
    doc.pop(\"_id\", None)
    return analysis


@api_router.get(\"/cases\", response_model=List[CaseAnalysis])
async def list_cases():
    docs = await db.cases.find({}, {\"_id\": 0}).sort(\"created_at\", -1).to_list(200)
    return docs


@api_router.get(\"/cases/{case_id}\", response_model=CaseAnalysis)
async def get_case(case_id: str):
    doc = await db.cases.find_one({\"case_id\": case_id}, {\"_id\": 0})
    if not doc:
        raise HTTPException(status_code=404, detail=\"Case not found\")
    return doc


# Mount router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=[\"*\"],
    allow_headers=[\"*\"],
)


@app.on_event(\"shutdown\")
async def shutdown_db_client():
    client.close()