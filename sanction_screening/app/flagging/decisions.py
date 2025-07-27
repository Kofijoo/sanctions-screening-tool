"""Decision types and workflow routing"""
from enum import Enum
from typing import Dict, Any
from datetime import datetime

class DecisionAction(Enum):
    """Possible compliance decisions"""
    AUTO_CLEAR = "AUTO_CLEAR"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    ESCALATE = "ESCALATE"
    BLOCK = "BLOCK"

class Priority(Enum):
    """Decision priority levels"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class DecisionMaker:
    """Create and validate compliance decisions"""
    
    def create_decision(self, action: str, reason: str, **kwargs) -> Dict[str, Any]:
        """Create a standardized decision object"""
        decision = {
            'action': action,
            'reason': reason,
            'timestamp': datetime.now().isoformat(),
            'confidence': kwargs.get('confidence', 'MEDIUM'),
            'priority': kwargs.get('priority', 'MEDIUM'),
            'requires_approval': self._requires_approval(action),
            'sla_hours': self._get_sla_hours(action, kwargs.get('priority', 'MEDIUM'))
        }
        
        # Add optional fields
        if 'assigned_to' in kwargs:
            decision['assigned_to'] = kwargs['assigned_to']
        if 'match_details' in kwargs:
            decision['match_details'] = kwargs['match_details']
        if 'filter_applied' in kwargs:
            decision['filter_applied'] = kwargs['filter_applied']
            
        return decision
    
    def _requires_approval(self, action: str) -> bool:
        """Check if decision requires supervisor approval"""
        approval_required = {
            DecisionAction.AUTO_CLEAR.value: False,
            DecisionAction.MANUAL_REVIEW.value: False,
            DecisionAction.ESCALATE.value: True,
            DecisionAction.BLOCK.value: True
        }
        return approval_required.get(action, True)
    
    def _get_sla_hours(self, action: str, priority: str) -> int:
        """Get SLA hours based on action and priority"""
        sla_matrix = {
            DecisionAction.AUTO_CLEAR.value: {'LOW': 0, 'MEDIUM': 0, 'HIGH': 0, 'CRITICAL': 0},
            DecisionAction.MANUAL_REVIEW.value: {'LOW': 72, 'MEDIUM': 24, 'HIGH': 8, 'CRITICAL': 2},
            DecisionAction.ESCALATE.value: {'LOW': 48, 'MEDIUM': 12, 'HIGH': 4, 'CRITICAL': 1},
            DecisionAction.BLOCK.value: {'LOW': 24, 'MEDIUM': 8, 'HIGH': 2, 'CRITICAL': 0}
        }
        
        return sla_matrix.get(action, {}).get(priority, 24)
    
    def validate_decision(self, decision: Dict[str, Any]) -> bool:
        """Validate decision structure and content"""
        required_fields = ['action', 'reason', 'timestamp', 'confidence', 'priority']
        
        # Check required fields
        for field in required_fields:
            if field not in decision:
                return False
        
        # Validate action
        valid_actions = [action.value for action in DecisionAction]
        if decision['action'] not in valid_actions:
            return False
        
        # Validate priority
        valid_priorities = [priority.value for priority in Priority]
        if decision['priority'] not in valid_priorities:
            return False
        
        return True
    
    def get_workflow_routing(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Get workflow routing information"""
        action = decision.get('action')
        priority = decision.get('priority', 'MEDIUM')
        
        routing = {
            DecisionAction.AUTO_CLEAR.value: {
                'queue': 'auto_processed',
                'notification': False,
                'escalation_path': None
            },
            DecisionAction.MANUAL_REVIEW.value: {
                'queue': 'analyst_review',
                'notification': True,
                'escalation_path': 'supervisor' if priority in ['HIGH', 'CRITICAL'] else None
            },
            DecisionAction.ESCALATE.value: {
                'queue': 'senior_analyst',
                'notification': True,
                'escalation_path': 'compliance_manager'
            },
            DecisionAction.BLOCK.value: {
                'queue': 'immediate_action',
                'notification': True,
                'escalation_path': 'compliance_manager'
            }
        }
        
        return routing.get(action, routing[DecisionAction.MANUAL_REVIEW.value])