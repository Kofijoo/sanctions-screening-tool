"""Test matching engine components"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.matching.similarity import SimilarityCalculator
from app.matching.matchers import ExactMatcher, FuzzyMatcher
from app.matching.engine import MatchingEngine
from app.preprocessing.processor import NameProcessor
from .test_data import create_sample_sanctions_data

def test_similarity_calculator():
    """Test similarity algorithms"""
    calc = SimilarityCalculator()
    
    # Test exact match
    score = calc.levenshtein_ratio("john smith", "john smith")
    assert score == 100.0, f"Exact match should be 100, got {score}"
    
    # Test similar names
    score = calc.levenshtein_ratio("john smith", "jon smith")
    assert score > 80.0, f"Similar names should score >80, got {score}"
    
    # Test different names
    score = calc.levenshtein_ratio("john smith", "jane doe")
    assert score < 50.0, f"Different names should score <50, got {score}"
    
    print("✅ Similarity calculator tests passed")

def test_exact_matcher():
    """Test exact matching"""
    matcher = ExactMatcher()
    
    # Test exact match
    result = matcher.match("john smith", "john smith")
    assert result['is_match'] == True
    assert result['score'] == 100.0
    
    # Test non-match
    result = matcher.match("john smith", "jane doe")
    assert result['is_match'] == False
    assert result['score'] == 0.0
    
    print("✅ Exact matcher tests passed")

def test_fuzzy_matcher():
    """Test fuzzy matching"""
    matcher = FuzzyMatcher()
    
    # Test similar names
    result = matcher.match("john smith", "jon smith")
    assert result['is_match'] == True
    assert result['score'] > 70.0
    
    # Test different names
    result = matcher.match("john smith", "jane doe")
    assert result['score'] < 60.0
    
    print("✅ Fuzzy matcher tests passed")

def test_matching_engine():
    """Test complete matching engine"""
    engine = MatchingEngine()
    processor = NameProcessor()
    
    # Create and preprocess sample data
    sanctions_df = create_sample_sanctions_data()
    sanctions_df = processor.process_dataframe(sanctions_df)
    
    # Test exact match
    result = engine.screen_name("Osama bin Laden", sanctions_df)
    assert len(result['matches']) > 0, "Should find matches for Osama bin Laden"
    assert result['summary']['highest_risk'] in ['HIGH', 'MEDIUM']
    
    # Test no match
    result = engine.screen_name("Jane Doe", sanctions_df)
    assert result['summary']['highest_risk'] == 'NONE'
    
    print("✅ Matching engine tests passed")

if __name__ == "__main__":
    test_similarity_calculator()
    test_exact_matcher()
    test_fuzzy_matcher()
    test_matching_engine()
    print("🎉 All matching tests passed!")