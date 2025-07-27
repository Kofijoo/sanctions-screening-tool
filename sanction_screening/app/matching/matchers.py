"""Different matching strategies for name screening"""
from typing import List, Dict, Any
from .similarity import SimilarityCalculator
from ..config import thresholds

class ExactMatcher:
    """Exact string matching after preprocessing"""
    
    def match(self, query: str, target: str) -> Dict[str, Any]:
        """Exact match check"""
        is_match = query.lower().strip() == target.lower().strip()
        
        return {
            'match_type': 'exact',
            'score': 100.0 if is_match else 0.0,
            'is_match': is_match,
            'details': {'exact_match': is_match}
        }

class FuzzyMatcher:
    """Fuzzy matching with configurable thresholds"""
    
    def __init__(self):
        self.similarity = SimilarityCalculator()
        
    def match(self, query: str, target: str) -> Dict[str, Any]:
        """Fuzzy match with detailed scoring"""
        score, details = self.similarity.weighted_average(query, target)
        
        # Determine match level based on thresholds
        if score >= thresholds.HIGH_RISK_THRESHOLD:
            match_level = 'high'
        elif score >= thresholds.MEDIUM_RISK_THRESHOLD:
            match_level = 'medium'
        elif score >= thresholds.LOW_RISK_THRESHOLD:
            match_level = 'low'
        else:
            match_level = 'none'
            
        return {
            'match_type': 'fuzzy',
            'score': score,
            'match_level': match_level,
            'is_match': score >= thresholds.LOW_RISK_THRESHOLD,
            'details': details
        }

class TokenMatcher:
    """Token-based matching for partial name matches"""
    
    def __init__(self):
        self.similarity = SimilarityCalculator()
        
    def match(self, query_tokens: List[str], target_tokens: List[str]) -> Dict[str, Any]:
        """Match individual tokens between names"""
        if not query_tokens or not target_tokens:
            return {
                'match_type': 'token',
                'score': 0.0,
                'is_match': False,
                'details': {'matched_tokens': []}
            }
        
        matched_tokens = []
        total_score = 0.0
        
        for q_token in query_tokens:
            best_match_score = 0.0
            best_match_token = None
            
            for t_token in target_tokens:
                token_score = self.similarity.levenshtein_ratio(q_token, t_token)
                if token_score > best_match_score:
                    best_match_score = token_score
                    best_match_token = t_token
            
            if best_match_score >= thresholds.LOW_RISK_THRESHOLD:
                matched_tokens.append({
                    'query': q_token,
                    'target': best_match_token,
                    'score': best_match_score
                })
                total_score += best_match_score
        
        # Average score of matched tokens
        avg_score = total_score / len(query_tokens) if query_tokens else 0.0
        
        return {
            'match_type': 'token',
            'score': avg_score,
            'is_match': avg_score >= thresholds.LOW_RISK_THRESHOLD,
            'details': {
                'matched_tokens': matched_tokens,
                'match_ratio': len(matched_tokens) / len(query_tokens)
            }
        }