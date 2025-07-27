"""Pydantic models for API requests and responses"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class ScreeningRequest(BaseModel):
    """Request model for name screening"""
    name: str = Field(..., min_length=2, max_length=200, description="Name to screen")
    batch_id: Optional[str] = Field(None, description="Optional batch identifier")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")

class BatchScreeningRequest(BaseModel):
    """Request model for batch screening"""
    names: List[str] = Field(..., min_items=1, max_items=1000, description="Names to screen")
    batch_id: Optional[str] = Field(None, description="Batch identifier")

class MatchResult(BaseModel):
    """Individual match result"""
    target_name: str
    source: str
    list_type: str
    score: float
    risk_score: float
    risk_level: str
    confidence: str
    match_type: str

class ScreeningResponse(BaseModel):
    """Response model for screening results"""
    screening_id: str
    query: str
    matches: List[MatchResult]
    decision: Dict[str, Any]
    summary: Dict[str, Any]
    processing_time_ms: float
    timestamp: datetime

class BatchScreeningResponse(BaseModel):
    """Response model for batch screening"""
    batch_id: str
    total_processed: int
    results: List[ScreeningResponse]
    summary: Dict[str, Any]
    processing_time_ms: float

class SystemStatus(BaseModel):
    """System status response"""
    status: str
    version: str
    sanctions_data: Dict[str, Any]
    last_update: Optional[datetime]
    uptime_seconds: float

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime