"""Audit data models for compliance logging"""
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any
import uuid

@dataclass
class LogEntry:
    """Single audit log entry for screening event"""
    screening_id: str
    timestamp: datetime
    event_type: str  # 'SCREENING', 'BATCH_SCREENING', 'SYSTEM_EVENT'
    query: str
    decision: str  # 'BLOCK', 'ESCALATE', 'MANUAL_REVIEW', 'AUTO_CLEAR'
    risk_level: str  # 'HIGH', 'MEDIUM', 'LOW', 'NONE'
    matches_count: int
    processing_time_ms: float
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    source_ip: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'screening_id': self.screening_id,
            'timestamp': self.timestamp.isoformat(),
            'event_type': self.event_type,
            'query': self.query,
            'decision': self.decision,
            'risk_level': self.risk_level,
            'matches_count': self.matches_count,
            'processing_time_ms': self.processing_time_ms,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'source_ip': self.source_ip
        }

@dataclass
class MatchEntry:
    """Audit entry for individual match details"""
    screening_id: str
    target_name: str
    source: str  # 'OFAC', 'UN', 'HMT', 'EU'
    match_score: float
    risk_score: float
    match_type: str  # 'exact', 'fuzzy', 'partial'
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'screening_id': self.screening_id,
            'target_name': self.target_name,
            'source': self.source,
            'match_score': self.match_score,
            'risk_score': self.risk_score,
            'match_type': self.match_type
        }