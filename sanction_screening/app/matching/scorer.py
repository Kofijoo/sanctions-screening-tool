"""Scoring and ranking system for matches"""
from typing import List, Dict, Any
from ..config import thresholds

class MatchScorer:
    """Score and rank matching results"""
    
    def calculate_risk_score(self, match_result: Dict[str, Any], list_source: str) -> float:
        """Calculate final risk score considering list priority"""
        base_score = match_result.get('score', 0.0)
        
        # Apply list priority multiplier
        list_priority = thresholds.LIST_PRIORITIES.get(list_source, 50)
        priority_multiplier = list_priority / 100.0
        
        # Boost exact matches
        if match_result.get('match_type') == 'exact':
            priority_multiplier *= 1.2
        
        final_score = min(base_score * priority_multiplier, 100.0)
        return final_score
    
    def determine_risk_level(self, score: float) -> str:
        """Determine risk level from score"""
        if score >= thresholds.HIGH_RISK_THRESHOLD:
            return 'HIGH'
        elif score >= thresholds.MEDIUM_RISK_THRESHOLD:
            return 'MEDIUM'
        elif score >= thresholds.LOW_RISK_THRESHOLD:
            return 'LOW'
        else:
            return 'NONE'
    
    def requires_review(self, score: float) -> bool:
        """Check if match requires manual review"""
        return score >= thresholds.REQUIRE_MANUAL_REVIEW_ABOVE
    
    def should_auto_clear(self, score: float) -> bool:
        """Check if match can be auto-cleared"""
        return score < thresholds.AUTO_CLEAR_BELOW
    
    def rank_matches(self, matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank matches by risk score (highest first)"""
        def sort_key(match):
            return (
                match.get('risk_score', 0.0),
                thresholds.LIST_PRIORITIES.get(match.get('source', ''), 0),
                match.get('score', 0.0)
            )
        
        return sorted(matches, key=sort_key, reverse=True)
    
    def create_match_summary(self, matches: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create summary of all matches"""
        if not matches:
            return {
                'total_matches': 0,
                'highest_risk': 'NONE',
                'requires_review': False,
                'can_auto_clear': True
            }
        
        highest_score = max(m.get('risk_score', 0.0) for m in matches)
        
        return {
            'total_matches': len(matches),
            'highest_risk': self.determine_risk_level(highest_score),
            'highest_score': highest_score,
            'requires_review': self.requires_review(highest_score),
            'can_auto_clear': self.should_auto_clear(highest_score),
            'risk_breakdown': {
                'HIGH': len([m for m in matches if self.determine_risk_level(m.get('risk_score', 0)) == 'HIGH']),
                'MEDIUM': len([m for m in matches if self.determine_risk_level(m.get('risk_score', 0)) == 'MEDIUM']),
                'LOW': len([m for m in matches if self.determine_risk_level(m.get('risk_score', 0)) == 'LOW'])
            }
        }