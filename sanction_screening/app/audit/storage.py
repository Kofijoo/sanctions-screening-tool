"""File-based audit storage for compliance records"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from .models import LogEntry, MatchEntry

class AuditStorage:
    """Handles persistent storage of audit logs"""
    
    def __init__(self, audit_dir: str = "data/audit"):
        self.audit_dir = Path(audit_dir)
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        
        # Separate files for different log types
        self.screening_log = self.audit_dir / "screening_events.jsonl"
        self.matches_log = self.audit_dir / "match_details.jsonl"
        self.system_log = self.audit_dir / "system_events.jsonl"
    
    def log_screening(self, entry: LogEntry) -> None:
        """Log screening event"""
        self._append_jsonl(self.screening_log, entry.to_dict())
    
    def log_matches(self, matches: List[MatchEntry]) -> None:
        """Log match details"""
        for match in matches:
            self._append_jsonl(self.matches_log, match.to_dict())
    
    def log_system_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """Log system events (startup, errors, etc.)"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'details': details
        }
        self._append_jsonl(self.system_log, event)
    
    def _append_jsonl(self, file_path: Path, data: Dict[str, Any]) -> None:
        """Append JSON line to file"""
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(data) + '\n')
    
    def get_recent_screenings(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent screening events"""
        if not self.screening_log.exists():
            return []
        
        entries = []
        with open(self.screening_log, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in reversed(lines[-limit:]):
                entries.append(json.loads(line.strip()))
        return entries