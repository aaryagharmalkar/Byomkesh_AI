# BYOMKESH AI

AI-Powered Forensic Analysis and Crime Scene Investigation Platform

## Overview

BYOMKESH AI is an intelligent system designed to assist law enforcement in analyzing First Information Reports (FIRs) and crime scene data. It extracts key facts, constructs forensic timelines, identifies logical connections, and suggests alternate scenarios—all powered by advanced reasoning and natural language processing.

## Features

- **Evidence Extraction**: Automatically identify times, locations, actors, entry/exit points, and stolen items
- **Timeline Reconstruction**: Build chronological event sequences distinguishing stated facts from inferred connections
- **Reasoning Engine**: Rule-based forensic logic combined with AI reasoning for scenario analysis
- **Alternate Scenarios**: Generate plausible alternative explanations with probability assessments
- **Confidence Scoring**: Weighted confidence metrics based on evidence completeness and logical consistency

Install the Python backend dependencies from the repository root:

```bash
pip install -r requirements.txt
```

Install the frontend dependencies:

```bash
cd app/frontend
npm install
```

## Run

Start the backend API:

```bash
cd app/backend
uvicorn server:app --reload --host 127.0.0.1 --port 8000
```

Start the frontend in a separate terminal:

```bash
cd app/frontend
npm start
```

The frontend runs on `http://localhost:3000` and talks to the backend at `http://127.0.0.1:8000` by default.

## Environment

Create or edit `app/backend/.env` with your API key. For demo mode, MongoDB is disabled in `server.py`, so the only required key is:

```dotenv
GROQ_API_KEY=your_groq_key_here
```

The existing `MONGO_URL` and `DB_NAME` entries can stay in place, but they are not used while demo storage is enabled.
