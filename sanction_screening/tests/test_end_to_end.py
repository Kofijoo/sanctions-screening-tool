"""End-to-end integration tests"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.preprocessing.processor import NameProcessor
from app.matching.engine import MatchingEngine
from app.flagging.engine import FlaggingEngine
from .test_data import create_sample_sanctions_data, get_test_queries

def test_full_screening_pipeline():
    """Test complete screening pipeline"""
    print("🔍 Testing full screening pipeline...")
    
    # Initialize components
    processor = NameProcessor()
    matching_engine = MatchingEngine()
    flagging_engine = FlaggingEngine()
    
    # Prepare sanctions data
    sanctions_df = create_sample_sanctions_data()
    sanctions_df = processor.process_dataframe(sanctions_df)
    
    print(f"📊 Loaded {len(sanctions_df)} sanctions entries")
    
    # Test each query
    test_queries = get_test_queries()
    
    for i, test_case in enumerate(test_queries, 1):
        query = test_case['query']
        expected_match = test_case['expected_match']
        
        print(f"\n{i}. Testing: '{query}'")
        
        # Step 1: Matching
        screening_result = matching_engine.screen_name(query, sanctions_df)
        
        # Step 2: Flagging
        final_result = flagging_engine.process_screening_result(screening_result)
        
        # Validate results
        has_matches = len(final_result['matches']) > 0
        decision = final_result['decision']['action']
        
        print(f"   Matches found: {len(final_result['matches'])}")
        print(f"   Decision: {decision}")
        print(f"   Risk level: {final_result['summary']['highest_risk']}")
        
        # Basic validation
        if expected_match:
            assert has_matches, f"Expected matches for '{query}' but found none"
        
        # Validate decision is reasonable
        valid_decisions = ['AUTO_CLEAR', 'MANUAL_REVIEW', 'ESCALATE', 'BLOCK']
        assert decision in valid_decisions, f"Invalid decision: {decision}"
        
        print(f"   ✅ Test passed")
    
    print("\n🎉 All end-to-end tests passed!")

def test_decision_logic():
    """Test decision logic with different scenarios"""
    print("\n🧠 Testing decision logic...")
    
    flagging_engine = FlaggingEngine()
    
    # Test high-risk scenario
    high_risk_result = {
        'query': 'Osama bin Laden',
        'matches': [{
            'target_name': 'Osama bin Laden',
            'source': 'OFAC',
            'match_type': 'exact',
            'score': 100.0,
            'risk_score': 100.0,
            'risk_level': 'HIGH'
        }],
        'summary': {
            'highest_risk': 'HIGH',
            'highest_score': 100.0,
            'requires_review': True,
            'can_auto_clear': False
        }
    }
    
    result = flagging_engine.process_screening_result(high_risk_result)
    decision = result['decision']['action']
    
    print(f"High-risk decision: {decision}")
    assert decision in ['BLOCK', 'ESCALATE'], f"High-risk should block/escalate, got {decision}"
    
    # Test low-risk scenario
    low_risk_result = {
        'query': 'Jane Doe',
        'matches': [],
        'summary': {
            'highest_risk': 'NONE',
            'highest_score': 0.0,
            'requires_review': False,
            'can_auto_clear': True
        }
    }
    
    result = flagging_engine.process_screening_result(low_risk_result)
    decision = result['decision']['action']
    
    print(f"Low-risk decision: {decision}")
    assert decision == 'AUTO_CLEAR', f"Low-risk should auto-clear, got {decision}"
    
    print("✅ Decision logic tests passed")

if __name__ == "__main__":
    test_full_screening_pipeline()
    test_decision_logic()
    print("\n🏆 All integration tests completed successfully!")