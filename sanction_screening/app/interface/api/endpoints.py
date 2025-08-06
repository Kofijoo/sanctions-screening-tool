"""FastAPI endpoints for SLST"""
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import time
from datetime import datetime
from typing import List
import uuid

from .models import (
    ScreeningRequest, ScreeningResponse, BatchScreeningRequest, 
    BatchScreeningResponse, SystemStatus, ErrorResponse
)
from ...preprocessing.processor import NameProcessor
from ...matching.engine import MatchingEngine
from ...flagging.engine import FlaggingEngine
from ...ingestion.manager import ListManager
from ...audit import audit_logger
from ...config import settings

app = FastAPI(
    title="SLST - Sanctions List Screening Tool",
    description="Production-grade compliance screening API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for web interface
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global components (in production, use dependency injection)
processor = NameProcessor()
matching_engine = MatchingEngine()
flagging_engine = FlaggingEngine()
list_manager = ListManager()

# Load sanctions data on startup
sanctions_data = None
startup_time = time.time()

@app.on_event("startup")
async def startup_event():
    """Initialize sanctions data on startup"""
    global sanctions_data
    try:
        print("🚀 Loading sanctions data...")
        list_data = list_manager.load_all()
        sanctions_data = list_manager.consolidate(list_data)
        sanctions_data = processor.process_dataframe(sanctions_data)
        sources = list(sanctions_data['source'].unique()) if len(sanctions_data) > 0 else []
        audit_logger.log_system_startup(len(sanctions_data), sources)
        print(f"✅ Loaded {len(sanctions_data)} sanctions entries")
    except Exception as e:
        audit_logger.log_error("STARTUP_ERROR", str(e))
        print(f"❌ Failed to load sanctions data: {e}")
        sanctions_data = processor.process_dataframe(list_manager.consolidate({}))

@app.get("/", response_class=HTMLResponse)
async def root():
    """Landing page with API documentation"""
    return """
    <html>
        <head><title>SLST - Sanctions Screening API</title></head>
        <body style="font-family: Arial; margin: 40px;">
            <h1>🛡️ SLST - Sanctions List Screening Tool</h1>
            <p><strong>Production-grade compliance screening API</strong></p>
            <ul>
                <li><a href="/docs">📖 Interactive API Documentation</a></li>
                <li><a href="/status">📊 System Status</a></li>
                <li><a href="/dashboard">🎛️ Web Dashboard</a></li>
            </ul>
            <h3>Quick Test:</h3>
            <p>POST /screen with: <code>{"name": "Osama bin Laden"}</code></p>
        </body>
    </html>
    """

@app.get("/status", response_model=SystemStatus)
async def get_status():
    """Get system status and health"""
    return SystemStatus(
        status="healthy" if sanctions_data is not None else "degraded",
        version="1.0.0",
        sanctions_data={
            "total_entries": len(sanctions_data) if sanctions_data is not None else 0,
            "sources": list(sanctions_data['source'].unique()) if sanctions_data is not None else []
        },
        last_update=datetime.now(),
        uptime_seconds=time.time() - startup_time
    )

@app.post("/screen", response_model=ScreeningResponse)
async def screen_name(request: ScreeningRequest):
    """Screen a single name against sanctions lists"""
    if sanctions_data is None:
        raise HTTPException(status_code=503, detail="Sanctions data not available")
    
    start_time = time.time()
    
    try:
        # Screen the name
        screening_result = matching_engine.screen_name(request.name, sanctions_data)
        final_result = flagging_engine.process_screening_result(screening_result)
        
        processing_time = (time.time() - start_time) * 1000
        
        # Log the screening event
        screening_id = audit_logger.log_screening(
            query=request.name,
            screening_result=final_result,
            processing_time_ms=processing_time
        )
        
        # Convert to response model
        matches = [
            {
                "target_name": match.get("target_name", ""),
                "source": match.get("source", ""),
                "list_type": match.get("list_type", ""),
                "score": match.get("score", 0.0),
                "risk_score": match.get("risk_score", 0.0),
                "risk_level": match.get("risk_level", "NONE"),
                "confidence": match.get("confidence", "LOW"),
                "match_type": match.get("match_type", "unknown")
            }
            for match in final_result.get("matches", [])
        ]
        
        return ScreeningResponse(
            screening_id=screening_id,
            query=request.name,
            matches=matches,
            decision=final_result.get("decision", {}),
            summary=final_result.get("summary", {}),
            processing_time_ms=processing_time,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        audit_logger.log_error("SCREENING_ERROR", str(e), {"query": request.name})
        raise HTTPException(status_code=500, detail=f"Screening failed: {str(e)}")

@app.post("/screen/batch", response_model=BatchScreeningResponse)
async def screen_batch(request: BatchScreeningRequest, background_tasks: BackgroundTasks):
    """Screen multiple names in batch"""
    if sanctions_data is None:
        raise HTTPException(status_code=503, detail="Sanctions data not available")
    
    start_time = time.time()
    batch_id = request.batch_id or str(uuid.uuid4())
    
    try:
        results = []
        
        for name in request.names:
            screening_result = matching_engine.screen_name(name, sanctions_data)
            final_result = flagging_engine.process_screening_result(screening_result)
            
            # Log individual screening in batch
            screening_id = audit_logger.log_screening(
                query=name,
                screening_result=final_result,
                processing_time_ms=0,  # Individual timing not calculated in batch
                session_id=batch_id
            )
            
            matches = [
                {
                    "target_name": match.get("target_name", ""),
                    "source": match.get("source", ""),
                    "list_type": match.get("list_type", ""),
                    "score": match.get("score", 0.0),
                    "risk_score": match.get("risk_score", 0.0),
                    "risk_level": match.get("risk_level", "NONE"),
                    "confidence": match.get("confidence", "LOW"),
                    "match_type": match.get("match_type", "unknown")
                }
                for match in final_result.get("matches", [])
            ]
            
            results.append(ScreeningResponse(
                screening_id=screening_id,
                query=name,
                matches=matches,
                decision=final_result.get("decision", {}),
                summary=final_result.get("summary", {}),
                processing_time_ms=0,
                timestamp=datetime.now()
            ))
        
        processing_time = (time.time() - start_time) * 1000
        
        # Calculate batch summary
        total_matches = sum(len(result.matches) for result in results)
        high_risk_count = sum(1 for result in results if result.summary.get("highest_risk") == "HIGH")
        
        batch_summary = {
            "total_matches": total_matches,
            "high_risk_cases": high_risk_count,
            "processing_rate": len(results) / (processing_time / 1000) if processing_time > 0 else 0
        }
        
        # Log batch completion
        audit_logger.log_batch_screening(batch_id, len(results), processing_time, batch_summary)
        
        return BatchScreeningResponse(
            batch_id=batch_id,
            total_processed=len(results),
            results=results,
            summary=batch_summary,
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        audit_logger.log_error("BATCH_SCREENING_ERROR", str(e), {"batch_id": batch_id})
        raise HTTPException(status_code=500, detail=f"Batch screening failed: {str(e)}")

@app.post("/admin/refresh-data")
async def refresh_sanctions_data(background_tasks: BackgroundTasks):
    """Refresh sanctions data (admin endpoint)"""
    background_tasks.add_task(reload_sanctions_data)
    return {"message": "Sanctions data refresh initiated"}

async def reload_sanctions_data():
    """Background task to reload sanctions data"""
    global sanctions_data
    try:
        list_data = list_manager.load_all()
        new_data = list_manager.consolidate(list_data)
        sanctions_data = processor.process_dataframe(new_data)
        sources = list(sanctions_data['source'].unique()) if len(sanctions_data) > 0 else []
        audit_logger.log_system_startup(len(sanctions_data), sources)
        print(f"✅ Refreshed {len(sanctions_data)} sanctions entries")
    except Exception as e:
        audit_logger.log_error("DATA_REFRESH_ERROR", str(e))
        print(f"❌ Failed to refresh sanctions data: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)