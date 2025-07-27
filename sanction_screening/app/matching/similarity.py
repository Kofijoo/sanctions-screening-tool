"""Core similarity algorithms for name matching"""
from rapidfuzz import fuzz
from typing import Tuple

class SimilarityCalculator:
    """Calculate similarity scores between names"""
    
    def levenshtein_ratio(self, str1: str, str2: str) -> float:
        """Levenshtein distance as ratio (0-100)"""
        if not str1 or not str2:
            return 0.0
        return fuzz.ratio(str1, str2)
    
    def partial_ratio(self, str1: str, str2: str) -> float:
        """Partial string matching ratio"""
        if not str1 or not str2:
            return 0.0
        return fuzz.partial_ratio(str1, str2)
    
    def token_sort_ratio(self, str1: str, str2: str) -> float:
        """Token sort ratio (order-independent)"""
        if not str1 or not str2:
            return 0.0
        return fuzz.token_sort_ratio(str1, str2)
    
    def token_set_ratio(self, str1: str, str2: str) -> float:
        """Token set ratio (handles duplicates)"""
        if not str1 or not str2:
            return 0.0
        return fuzz.token_set_ratio(str1, str2)
    
    def weighted_average(self, str1: str, str2: str) -> Tuple[float, dict]:
        """Weighted average of all similarity measures"""
        scores = {
            'levenshtein': self.levenshtein_ratio(str1, str2),
            'partial': self.partial_ratio(str1, str2),
            'token_sort': self.token_sort_ratio(str1, str2),
            'token_set': self.token_set_ratio(str1, str2)
        }
        
        # Weights based on compliance effectiveness
        weights = {
            'levenshtein': 0.3,
            'partial': 0.2,
            'token_sort': 0.3,
            'token_set': 0.2
        }
        
        weighted_score = sum(scores[key] * weights[key] for key in scores)
        
        return weighted_score, scores