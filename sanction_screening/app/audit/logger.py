"""Main audit logger for SLST compliance tracking"""
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from .models import LogEntry, MatchEntry
from .storage import AuditStorage

class AuditLogger:
    """Central audit logging system for compliance"""
    
    def __init__(self, storage: Optional[AuditStorage] = None):
        self.storage = storage or AuditStorage()
    
    def log_screening(
        self,
        query: str,
        screening_result: Dict[str, Any],
        processing_time_ms: float,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        source_ip: Optional[str] = None
    ) -> str:
        """Log a screening event and return screening_id"""
        
        screening_id = str(uuid.uuid4())
        
        # Extract key information from screening result
        decision = screening_result.get('decision', {}).get('action', 'UNKNOWN')
        risk_level = screening_result.get('summary', {}).get('highest_risk', 'NONE')
        matches = screening_result.get('matches', [])
        
        # Create main log entry
        log_entry = LogEntry(
            screening_id=screening_id,
            timestamp=datetime.now(),
            event_type='SCREENING',
            query=query,
            decision=decision,
            risk_level=risk_level,
            matches_count=len(matches),
            processing_time_ms=processing_time_ms,
            user_id=user_id,
            session_id=session_id,
            source_ip=source_ip
        )
        
        # Log the screening event
        self.storage.log_screening(log_entry)
        
        # Log match details if any
        if matches:
            match_entries = []
            for match in matches:
                match_entry = MatchEntry(
                    screening_id=screening_id,
                    target_name=match.get('target_name', ''),
                    source=match.get('source', ''),
                    match_score=match.get('score', 0.0),
                    risk_score=match.get('risk_score', 0.0),
                    match_type=match.get('match_type', 'unknown')
                )
                match_entries.append(match_entry)
            
            self.storage.log_matches(match_entries)
        
        return screening_id
    
    def log_batch_screening(
        self,
        batch_id: str,
        total_processed: int,
        processing_time_ms: float,
        summary: Dict[str, Any]
    ) -> None:
        """Log batch screening completion"""
        self.storage.log_system_event('BATCH_SCREENING', {
            'batch_id': batch_id,
            'total_processed': total_processed,
            'processing_time_ms': processing_time_ms,
            'summary': summary
        })
    
    def log_system_startup(self, sanctions_count: int, sources: List[str]) -> None:
        """Log system startup"""
        self.storage.log_system_event('SYSTEM_STARTUP', {
            'sanctions_count': sanctions_count,
            'sources': sources
        })
    
    def log_error(self, error_type: str, error_message: str, context: Dict[str, Any] = None) -> None:
        """Log system errors"""
        self.storage.log_system_event('ERROR', {
            'error_type': error_type,
            'error_message': error_message,
            'context': context or {}
        })

# Global audit logger instance
audit_logger = AuditLogger()