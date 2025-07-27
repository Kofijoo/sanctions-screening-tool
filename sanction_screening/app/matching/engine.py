"""Main matching engine orchestration"""
import pandas as pd
from typing import List, Dict, Any
from .matchers import ExactMatcher, FuzzyMatcher, TokenMatcher
from .scorer import MatchScorer
from ..preprocessing.processor import NameProcessor
from ..config import thresholds

class MatchingEngine:
    """Main engine for sanctions list matching"""
    
    def __init__(self):
        self.processor = NameProcessor()
        self.exact_matcher = ExactMatcher()
        self.fuzzy_matcher = FuzzyMatcher()
        self.token_matcher = TokenMatcher()
        self.scorer = MatchScorer()
        
    def screen_name(self, query_name: str, sanctions_df: pd.DataFrame) -> Dict[str, Any]:
        """Screen a single name against sanctions list"""
        if not query_name or len(query_name.strip()) < thresholds.MIN_NAME_LENGTH:
            return {
                'query': query_name,
                'matches': [],
                'summary': self.scorer.create_match_summary([])
            }
        
        # Preprocess query name
        query_processed = self.processor.process_single(query_name)
        
        matches = []
        
        # Screen against each sanctions entry
        for _, sanction_row in sanctions_df.iterrows():
            match_results = self._match_against_entry(query_processed, sanction_row)
            
            if match_results:
                matches.extend(match_results)
        
        # Score and rank matches
        for match in matches:
            match['risk_score'] = self.scorer.calculate_risk_score(
                match, match.get('source', '')
            )
            match['risk_level'] = self.scorer.determine_risk_level(match['risk_score'])
        
        # Filter out low-scoring matches
        significant_matches = [
            m for m in matches 
            if m.get('risk_score', 0) >= thresholds.LOW_RISK_THRESHOLD
        ]
        
        # Rank by risk score
        ranked_matches = self.scorer.rank_matches(significant_matches)
        
        return {
            'query': query_name,
            'processed_query': query_processed,
            'matches': ranked_matches,
            'summary': self.scorer.create_match_summary(ranked_matches)
        }
    
    def _match_against_entry(self, query_processed: Dict, sanction_row: pd.Series) -> List[Dict[str, Any]]:
        """Match query against single sanctions entry"""
        matches = []
        
        sanction_name = sanction_row.get('normalized', sanction_row.get('name', ''))
        if not sanction_name:
            return matches
        
        # Try exact match first
        exact_result = self.exact_matcher.match(
            query_processed['normalized'], 
            sanction_name
        )
        
        if exact_result['is_match']:
            matches.append({
                **exact_result,
                'target_name': sanction_row.get('name', ''),
                'source': sanction_row.get('source', ''),
                'list_type': sanction_row.get('list_type', ''),
                'confidence': 'HIGH'
            })
            return matches  # Exact match found, no need for fuzzy
        
        # Try fuzzy match
        fuzzy_result = self.fuzzy_matcher.match(
            query_processed['normalized'],
            sanction_name
        )
        
        if fuzzy_result['is_match']:
            matches.append({
                **fuzzy_result,
                'target_name': sanction_row.get('name', ''),
                'source': sanction_row.get('source', ''),
                'list_type': sanction_row.get('list_type', ''),
                'confidence': fuzzy_result['match_level'].upper()
            })
        
        # Try token match for partial matches
        sanction_tokens = sanction_row.get('tokens', [])
        if sanction_tokens:
            token_result = self.token_matcher.match(
                query_processed['tokens'],
                sanction_tokens
            )
            
            if token_result['is_match']:
                matches.append({
                    **token_result,
                    'target_name': sanction_row.get('name', ''),
                    'source': sanction_row.get('source', ''),
                    'list_type': sanction_row.get('list_type', ''),
                    'confidence': 'MEDIUM'
                })
        
        return matches