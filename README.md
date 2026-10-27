# Intentify — AI Prompt Intelligence Platform

> Convert any human input into a premium professional Master Prompt using local AI models and custom ML pipelines.

## Architecture

```
intentify/
├── backend/           # FastAPI backend with clean architecture
│   └── app/
│       ├── core/      # Configuration, security, exceptions
│       ├── config/    # Application settings
│       ├── api/       # REST API endpoints (v1)
│       ├── services/  # Business logic orchestration
│       ├── compiler/  # Prompt compilation engine
│       ├── nlp/       # NLP processing pipeline
│       ├── ml/        # ML model management
│       ├── knowledge/ # Knowledge base integration
│       ├── quality/   # Quality evaluation engine
│       ├── workers/   # Background task workers
│       └── utils/     # Utility functions
├── frontend/          # Next.js frontend
├── ml-engine/         # ML training pipeline
│   ├── training/      # Model training scripts
│   ├── datasets/      # Training datasets
│   ├── models/        # Trained model artifacts
│   └── evaluation/    # Model evaluation tools
├── knowledge-base/    # Knowledge base (JSON)
│   ├── roles/         # Professional role definitions
│   ├── domains/       # Domain knowledge
│   ├── blueprints/    # Prompt blueprints by intent
│   ├── templates/     # Output format templates
│   ├── quality_rules/ # Quality scoring rules
│   └── assumptions/   # Default assumptions
└── tests/             # Comprehensive test suite
```

## AI Intelligence Layers

1. **Language Intelligence** — Multilingual detection, script identification, transliteration
2. **NLP Understanding** — Intent classification, role extraction, entity recognition
3. **Domain Intelligence** — Unlimited domain detection via embeddings + knowledge graph
4. **Requirement Extraction** — Goal, audience, tone, format, constraints extraction
5. **Prompt Compilation** — Blueprint-based intelligent prompt assembly
6. **Quality Evaluation** — 100-point scoring with auto-improvement loop

## Technology Stack

### Backend
- Python 3.11+ / FastAPI / Pydantic v2 / SQLAlchemy / PostgreSQL / Redis

### Frontend
- Next.js / TypeScript / Tailwind CSS / shadcn/ui / React Query

### ML/AI (All Local)
- PyTorch / Transformers / Sentence Transformers
- FastText language identification
- Custom trained classifiers (intent, domain, role, quality)
- Local embedding models (multilingual-e5 / BGE)

## Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### ML Training
```bash
cd ml-engine
python -m training.trainer --task all
```

## API

### POST /api/v1/generate-prompt

**Request:**
```json
{
  "role": "Software Engineer",
  "detail": "Build a REST API for user authentication",
  "language": "en",
  "tone": "professional",
  "format": "detailed"
}
```

**Response:**
```json
{
  "master_prompt": "...",
  "assumptions": ["..."],
  "quality_score": 92.5,
  "improvements": ["..."],
  "metadata": {
    "detected_language": "en",
    "detected_intent": "create",
    "detected_domain": "Software Development",
    "processing_time_ms": 245.3
  }
}
```

## License

Proprietary — All rights reserved.
