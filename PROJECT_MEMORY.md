# Sanction List Screening Tool (SLST) - Project Memory

## Project Overview
- **Name**: Sanction List Screening Tool (SLST)
- **Objective**: Screen individual/entity names against global sanctions lists using NLP and fuzzy matching
- **Context**: Production-grade compliance tool for banks/fintech under regulatory scrutiny
- **Approach**: Step-by-step development with full understanding at each stage

## Technology Stack Approved
- **Language**: Python 3.10+
- **Environment**: Docker, pipenv/poetry
- **Data**: Pandas, PyArrow
- **Matching**: rapidfuzz, textdistance, polyfuzz
- **NLP**: spaCy or HuggingFace
- **UI**: FastAPI + React or Streamlit
- **Database**: PostgreSQL
- **Deployment**: Docker Compose/Kubernetes

## Directory Structure Plan
```
sanction_screening/
├── app/
│   ├── config/
│   ├── ingestion/
│   ├── preprocessing/
│   ├── matching/
│   ├── flagging/
│   ├── interface/
│   └── audit/
├── tests/
├── data/
├── scripts/
├── notebooks/
└── deployment files
```

## Development Progress
- [x] Step 1: Project setup and environment
- [x] Step 2: Basic directory structure
- [x] Step 3: Configuration management
- [x] Step 4: Data ingestion layer
- [x] Step 5: Preprocessing engine
- [x] Step 6: Matching engine
- [x] Step 7: Flagging engine
- [x] Step 8: User interface
- [ ] Step 9: Audit and logging
- [ ] Step 10: Testing and deployment

## Current Status
- **Phase**: Planning Complete
- **Next Step**: Awaiting confirmation to begin Step 1
- **Notes**: All abbreviations explained, comprehensive plan documented