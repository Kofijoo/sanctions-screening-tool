"""Test runner for SLST"""
import sys
import os

# Add app to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def run_all_tests():
    """Run all test suites"""
    print("🚀 Starting SLST Test Suite")
    print("=" * 50)
    
    try:
        # Test 1: Preprocessing
        print("\n📝 Testing Preprocessing Components...")
        from tests.test_preprocessing import (
            test_text_cleaner, 
            test_name_normalizer, 
            test_name_processor
        )
        test_text_cleaner()
        test_name_normalizer()
        test_name_processor()
        
        # Test 2: Matching
        print("\n🎯 Testing Matching Components...")
        from tests.test_matching import (
            test_similarity_calculator,
            test_exact_matcher,
            test_fuzzy_matcher,
            test_matching_engine
        )
        test_similarity_calculator()
        test_exact_matcher()
        test_fuzzy_matcher()
        test_matching_engine()
        
        # Test 3: End-to-End
        print("\n🔄 Testing End-to-End Integration...")
        from tests.test_end_to_end import (
            test_full_screening_pipeline,
            test_decision_logic
        )
        test_full_screening_pipeline()
        test_decision_logic()
        
        print("\n" + "=" * 50)
        print("🎉 ALL TESTS PASSED! 🎉")
        print("✅ Your SLST system is working correctly")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        print("🔧 Check the error above and fix the issue")
        return False
    
    return True

def run_quick_demo():
    """Run a quick demonstration"""
    print("\n🎬 Quick Demo - Screening Sample Names")
    print("-" * 40)
    
    try:
        from app.preprocessing.processor import NameProcessor
        from app.matching.engine import MatchingEngine
        from app.flagging.engine import FlaggingEngine
        from tests.test_data import create_sample_sanctions_data
        
        # Setup
        processor = NameProcessor()
        matching_engine = MatchingEngine()
        flagging_engine = FlaggingEngine()
        
        sanctions_df = create_sample_sanctions_data()
        sanctions_df = processor.process_dataframe(sanctions_df)
        
        # Demo queries
        demo_queries = [
            "Osama bin Laden",
            "Al Qaeda", 
            "John Smith",
            "Jane Doe"
        ]
        
        for query in demo_queries:
            print(f"\n🔍 Screening: '{query}'")
            
            # Screen the name
            screening_result = matching_engine.screen_name(query, sanctions_df)
            final_result = flagging_engine.process_screening_result(screening_result)
            
            # Show results
            matches = len(final_result['matches'])
            decision = final_result['decision']['action']
            risk = final_result['summary']['highest_risk']
            
            print(f"   📊 Matches: {matches}")
            print(f"   ⚖️  Decision: {decision}")
            print(f"   🚨 Risk Level: {risk}")
            
            if matches > 0:
                best_match = final_result['matches'][0]
                print(f"   🎯 Best Match: {best_match['target_name']} ({best_match['source']})")
        
        print("\n✨ Demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")

if __name__ == "__main__":
    print("Choose an option:")
    print("1. Run all tests")
    print("2. Run quick demo")
    print("3. Run both")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        run_all_tests()
    elif choice == "2":
        run_quick_demo()
    elif choice == "3":
        run_all_tests()
        run_quick_demo()
    else:
        print("Invalid choice. Running all tests...")
        run_all_tests()