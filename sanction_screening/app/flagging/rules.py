"""Business rules engine for compliance decisions"""
from typing import Dict, Any, List
from ..config import thresholds

class BusinessRules:
    """Business rules for compliance decision making"""
    
    def __init__(self):
        self.rules = {
            'exact_ofac_block': self._exact_ofac_block,
            'high_risk_escalate': self._high_risk_escalate,
            'medium_risk_review': self._medium_risk_review,
            'low_risk_clear': self._low_risk_clear,
            'common_name_filter': self._common_name_filter
        }
    
    def apply_rules(self, screening_result: Dict[str, Any]) -> Dict[str, Any]:
        """Apply all business rules to screening result"""
        matches = screening_result.get('matches', [])
        summary = screening_result.get('summary', {})
        
        # Apply rules in priority order
        for rule_name, rule_func in self.rules.items():
            decision = rule_func(matches, summary, screening_result)
            if decision:
                return {
                    **screening_result,
                    'decision': decision,
                    'applied_rule': rule_name
                }
        
        # Default decision if no rules match
        return {
            **screening_result,
            'decision': {
                'action': 'AUTO_CLEAR',
                'reason': 'No significant matches found',
                'confidence': 'HIGH',
                'priority': 'LOW',
                'timestamp': 'auto-generated'
            },
            'applied_rule': 'default'
        }
    
    def _exact_ofac_block(self, matches: List[Dict], summary: Dict, result: Dict) -> Dict[str, Any]:
        """Block immediately for exact OFAC matches"""
        for match in matches:
            if (match.get('source') == 'OFAC' and 
                match.get('match_type') == 'exact' and
                (match.get('score', 0) == 100.0 or match.get('risk_score', 0) == 100.0)):
                
                return {
                    'action': 'BLOCK',
                    'reason': f'Exact OFAC match: {match.get("target_name")}',
                    'confidence': 'HIGH',
                    'priority': 'CRITICAL',
                    'timestamp': 'auto-generated',
                    'match_details': match
                }
        return None
    
    def _high_risk_escalate(self, matches: List[Dict], summary: Dict, result: Dict) -> Dict[str, Any]:
        """Escalate high-risk matches to senior analysts"""
        highest_score = summary.get('highest_score', 0)
        
        if highest_score >= 85.0:  # High confidence threshold
            high_risk_match = max(matches, key=lambda m: m.get('risk_score', 0))
            
            return {
                'action': 'ESCALATE',
                'reason': f'High-risk match (score: {highest_score:.1f})',
                'confidence': 'HIGH',
                'priority': 'HIGH',
                'timestamp': 'auto-generated',
                'assigned_to': 'senior_analyst',
                'match_details': high_risk_match
            }
        return None
    
    def _medium_risk_review(self, matches: List[Dict], summary: Dict, result: Dict) -> Dict[str, Any]:
        """Route medium-risk matches for manual review"""
        highest_score = summary.get('highest_score', 0)
        
        # Only route to manual review if not high-risk
        if summary.get('requires_review', False) and highest_score < 85.0:
            best_match = matches[0] if matches else None
            
            return {
                'action': 'MANUAL_REVIEW',
                'reason': f'Medium-risk match requires review',
                'confidence': 'MEDIUM',
                'priority': 'MEDIUM',
                'assigned_to': 'analyst',
                'match_details': best_match
            }
        return None
    
    def _low_risk_clear(self, matches: List[Dict], summary: Dict, result: Dict) -> Dict[str, Any]:
        """Auto-clear low-risk matches"""
        if summary.get('can_auto_clear', False):
            return {
                'action': 'AUTO_CLEAR',
                'reason': 'Low risk score, auto-cleared',
                'confidence': 'MEDIUM',
                'priority': 'LOW',
                'timestamp': 'auto-generated'
            }
        return None
    
    def _common_name_filter(self, matches: List[Dict], summary: Dict, result: Dict) -> Dict[str, Any]:
        """Filter common names that are likely false positives"""
        query = result.get('query', '').lower().strip()
        
        # Common names that generate false positives
        common_names = {
            'john smith', 'mary johnson', 'david brown', 'michael davis',
            'james wilson', 'robert miller', 'william moore', 'richard taylor'
        }
        
        if query in common_names and summary.get('highest_score', 0) < 80.0:
            return {
                'action': 'AUTO_CLEAR',
                'reason': 'Common name with low confidence match',
                'confidence': 'MEDIUM',
                'priority': 'LOW',
                'filter_applied': 'common_name'
            }
        return None