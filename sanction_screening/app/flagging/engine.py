"""Main flagging engine orchestration"""
from typing import Dict, Any
from .rules import BusinessRules
from .decisions import DecisionMaker
from .filters import FalsePositiveFilter

class FlaggingEngine:
    """Main engine for compliance flagging and decision making"""
    
    def __init__(self):
        self.business_rules = BusinessRules()
        self.decision_maker = DecisionMaker()
        self.fp_filter = FalsePositiveFilter()
        
    def process_screening_result(self, screening_result: Dict[str, Any]) -> Dict[str, Any]:
        """Process screening result through flagging pipeline"""
        
        # Step 1: Apply false positive filters
        original_matches = screening_result.get('matches', [])
        filtered_matches = self.fp_filter.apply_filters(
            original_matches, 
            screening_result.get('query', '')
        )
        
        # Update screening result with filtered matches
        screening_result['matches'] = filtered_matches
        screening_result['filtered_count'] = len(original_matches) - len(filtered_matches)
        
        # Step 2: Apply business rules to make decision
        flagged_result = self.business_rules.apply_rules(screening_result)
        
        # Step 3: Validate and enhance decision
        decision = flagged_result.get('decision', {})
        if self.decision_maker.validate_decision(decision):
            # Add workflow routing information
            decision['workflow'] = self.decision_maker.get_workflow_routing(decision)
            flagged_result['decision'] = decision
        else:
            # Fallback decision if validation fails
            flagged_result['decision'] = self.decision_maker.create_decision(
                'MANUAL_REVIEW',
                'Decision validation failed, routing for manual review',
                priority='MEDIUM'
            )
        
        # Step 4: Add compliance metadata
        flagged_result['compliance'] = self._generate_compliance_metadata(flagged_result)
        
        return flagged_result
    
    def _generate_compliance_metadata(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate compliance metadata for audit trail"""
        decision = result.get('decision', {})
        matches = result.get('matches', [])
        
        metadata = {
            'screening_id': self._generate_screening_id(),
            'total_matches_found': len(result.get('matches', [])) + result.get('filtered_count', 0),
            'matches_after_filtering': len(matches),
            'highest_risk_score': max([m.get('risk_score', 0) for m in matches], default=0),
            'decision_action': decision.get('action'),
            'decision_confidence': decision.get('confidence'),
            'requires_approval': decision.get('requires_approval', False),
            'sla_hours': decision.get('sla_hours', 24),
            'applied_rule': result.get('applied_rule'),
            'processing_time_ms': 0  # Would be calculated in real implementation
        }
        
        # Add risk assessment
        if matches:
            metadata['risk_assessment'] = {
                'primary_concern': matches[0].get('source', 'Unknown'),
                'match_type': matches[0].get('match_type', 'Unknown'),
                'confidence_level': matches[0].get('confidence', 'MEDIUM')
            }
        
        return metadata
    
    def _generate_screening_id(self) -> str:
        """Generate unique screening ID for audit trail"""
        import uuid
        from datetime import datetime
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        
        return f"SLST_{timestamp}_{unique_id}"
    
    def get_decision_summary(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Get human-readable decision summary"""
        decision = result.get('decision', {})
        compliance = result.get('compliance', {})
        
        return {
            'screening_id': compliance.get('screening_id'),
            'query_name': result.get('query'),
            'decision': decision.get('action'),
            'reason': decision.get('reason'),
            'priority': decision.get('priority'),
            'requires_review': decision.get('action') in ['MANUAL_REVIEW', 'ESCALATE'],
            'immediate_action': decision.get('action') == 'BLOCK',
            'matches_found': compliance.get('matches_after_filtering', 0),
            'highest_score': compliance.get('highest_risk_score', 0),
            'sla_deadline': f"{decision.get('sla_hours', 24)} hours"
        }