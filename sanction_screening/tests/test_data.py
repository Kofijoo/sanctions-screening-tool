"""Sample test data for SLST testing"""
import pandas as pd

def create_sample_sanctions_data():
    """Create sample sanctions data for testing"""
    sample_data = [
        {
            'name': 'Osama bin Laden',
            'source': 'OFAC',
            'list_type': 'SDN',
            'date_added': '2024-01-01'
        },
        {
            'name': 'Al-Qaeda',
            'source': 'OFAC', 
            'list_type': 'SDN',
            'date_added': '2024-01-01'
        },
        {
            'name': 'John Smith',
            'source': 'UN',
            'list_type': 'Individual',
            'date_added': '2024-01-01'
        },
        {
            'name': 'Mohammed Al-Rashid',
            'source': 'HMT',
            'list_type': 'Individual', 
            'date_added': '2024-01-01'
        },
        {
            'name': 'Acme Corporation Ltd',
            'source': 'EU',
            'list_type': 'Entity',
            'date_added': '2024-01-01'
        }
    ]
    
    return pd.DataFrame(sample_data)

def get_test_queries():
    """Get test query names with expected results"""
    return [
        {
            'query': 'Osama bin Laden',
            'expected_match': True,
            'expected_source': 'OFAC',
            'expected_risk': 'HIGH'
        },
        {
            'query': 'Usama Bin Ladin',  # Variation
            'expected_match': True,
            'expected_source': 'OFAC',
            'expected_risk': 'HIGH'
        },
        {
            'query': 'Al Qaeda',  # No hyphen
            'expected_match': True,
            'expected_source': 'OFAC',
            'expected_risk': 'HIGH'
        },
        {
            'query': 'Jon Smith',  # Similar to John Smith
            'expected_match': True,
            'expected_source': 'UN',
            'expected_risk': 'MEDIUM'
        },
        {
            'query': 'Jane Doe',  # Should not match
            'expected_match': False,
            'expected_source': None,
            'expected_risk': 'NONE'
        }
    ]