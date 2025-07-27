"""Debug the business rules issue"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.flagging.engine import FlaggingEngine

def debug_business_rules():
    """Debug what's happening in business rules"""
    
    flagging_engine = FlaggingEngine()
    
    # Test high-risk scenario (same as in test)
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
    
    print("Debug: Input data structure")
    print(f"Matches: {high_risk_result['matches']}")
    print(f"Summary: {high_risk_result['summary']}")
    
    # Process through flagging engine
    result = flagging_engine.process_screening_result(high_risk_result)
    
    print(f"\nDebug: Final decision")
    print(f"Decision: {result['decision']['action']}")
    print(f"Applied rule: {result.get('applied_rule')}")
    print(f"Reason: {result['decision']['reason']}")
    
    # Test each rule individually
    print(f"\nDebug: Testing individual rules")
    business_rules = flagging_engine.business_rules
    
    matches = high_risk_result['matches']
    summary = high_risk_result['summary']
    
    for rule_name, rule_func in business_rules.rules.items():
        decision = rule_func(matches, summary, high_risk_result)
        print(f"{rule_name}: {decision['action'] if decision else 'None'}")

if __name__ == "__main__":
    debug_business_rules()