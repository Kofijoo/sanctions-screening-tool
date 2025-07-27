"""False positive reduction filters"""
from typing import List, Dict, Any
import re

class FalsePositiveFilter:
    """Reduce false positives through intelligent filtering"""
    
    def __init__(self):
        self.filters = {
            'common_words': self._filter_common_words,
            'short_names': self._filter_short_names,
            'title_only': self._filter_title_only_matches,
            'partial_weak': self._filter_weak_partial_matches,
            'geographic': self._filter_geographic_false_positives
        }
    
    def apply_filters(self, matches: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """Apply all false positive filters"""
        filtered_matches = matches.copy()
        
        for filter_name, filter_func in self.filters.items():
            filtered_matches = filter_func(filtered_matches, query)
            
        return filtered_matches
    
    def _filter_common_words(self, matches: List[Dict], query: str) -> List[Dict]:
        """Filter matches on very common words"""
        common_words = {
            'company', 'corporation', 'limited', 'ltd', 'inc', 'llc',
            'bank', 'group', 'international', 'trading', 'services',
            'foundation', 'association', 'organization', 'society'
        }
        
        query_lower = query.lower()
        
        filtered = []
        for match in matches:
            target_name = match.get('target_name', '').lower()
            
            # If match is only on common business words, filter out low scores
            if (any(word in query_lower for word in common_words) and
                any(word in target_name for word in common_words) and
                match.get('score', 0) < 75.0):
                
                match['filtered'] = True
                match['filter_reason'] = 'Common business word match'
            else:
                filtered.append(match)
                
        return filtered
    
    def _filter_short_names(self, matches: List[Dict], query: str) -> List[Dict]:
        """Filter matches on very short names"""
        if len(query.strip()) <= 3:
            return []  # Don't match very short queries
        
        filtered = []
        for match in matches:
            target_name = match.get('target_name', '')
            
            # Filter short target names with low scores
            if len(target_name.strip()) <= 3 and match.get('score', 0) < 90.0:
                match['filtered'] = True
                match['filter_reason'] = 'Short name with low confidence'
            else:
                filtered.append(match)
                
        return filtered
    
    def _filter_title_only_matches(self, matches: List[Dict], query: str) -> List[Dict]:
        """Filter matches that only match on titles/honorifics"""
        titles = {'mr', 'mrs', 'ms', 'dr', 'prof', 'sir', 'lady', 'lord'}
        
        query_words = set(query.lower().split())
        
        filtered = []
        for match in matches:
            target_words = set(match.get('target_name', '').lower().split())
            
            # Check if match is primarily on titles
            common_words = query_words & target_words
            title_words = common_words & titles
            
            if (len(title_words) > 0 and 
                len(title_words) / len(common_words) > 0.5 and
                match.get('score', 0) < 80.0):
                
                match['filtered'] = True
                match['filter_reason'] = 'Title-only match'
            else:
                filtered.append(match)
                
        return filtered
    
    def _filter_weak_partial_matches(self, matches: List[Dict], query: str) -> List[Dict]:
        """Filter weak partial matches"""
        filtered = []
        
        for match in matches:
            match_type = match.get('match_type', '')
            score = match.get('score', 0)
            
            # Filter weak token matches
            if (match_type == 'token' and 
                score < 70.0 and
                match.get('details', {}).get('match_ratio', 0) < 0.6):
                
                match['filtered'] = True
                match['filter_reason'] = 'Weak partial match'
            else:
                filtered.append(match)
                
        return filtered
    
    def _filter_geographic_false_positives(self, matches: List[Dict], query: str) -> List[Dict]:
        """Filter geographic false positives"""
        # Common geographic terms that cause false positives
        geographic_terms = {
            'north', 'south', 'east', 'west', 'central', 'new', 'old',
            'city', 'town', 'village', 'county', 'state', 'province',
            'republic', 'kingdom', 'emirates', 'federation'
        }
        
        query_lower = query.lower()
        
        filtered = []
        for match in matches:
            target_name = match.get('target_name', '').lower()
            
            # Check if match is primarily geographic
            query_geo_words = sum(1 for term in geographic_terms if term in query_lower)
            target_geo_words = sum(1 for term in geographic_terms if term in target_name)
            
            if (query_geo_words > 0 and target_geo_words > 0 and
                match.get('score', 0) < 75.0):
                
                match['filtered'] = True
                match['filter_reason'] = 'Geographic false positive'
            else:
                filtered.append(match)
                
        return filtered