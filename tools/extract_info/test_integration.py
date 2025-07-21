#!/usr/bin/env python3
"""
Test the integration between patient_client and no_llm_dateparser
"""

import json
from no_llm_dateparser import ComplexDateParser

def test_date_parser_integration():
    """Test the date parser with sample timeframe expressions"""
    
    parser = ComplexDateParser()
    
    test_cases = [
        "past two months",
        "last 2 days", 
        "past 2 years",
        "on 10th november",
        "on november 10",
        "from 10th july",
        "july 10th onwards",
        "since 10 july"
    ]
    
    print("Testing Date Parser Integration")
    print("=" * 50)
    
    for case in test_cases:
        print(f"\nInput: '{case}'")
        result = parser.parse_date_expression(case)
        
        # Simulate the patient_client processing (extract only date part)
        if result and result.get('type') in ['date_range', 'single_date']:
            if result.get('type') == 'single_date' and 'date' in result:
                # Handle single date case - extract only date part (YYYY-MM-DD)
                date_only = result['date'].split('T')[0]
                timeframe = {
                    "date": date_only
                }
                print(f"Output: {json.dumps(timeframe, indent=2)}")
            elif result.get('type') == 'date_range' and 'start_date' in result and 'end_date' in result:
                # Handle date range case - extract only date parts (YYYY-MM-DD)
                start_date_only = result['start_date'].split('T')[0]
                end_date_only = result['end_date'].split('T')[0]
                timeframe = {
                    "start_date": start_date_only,
                    "end_date": end_date_only
                }
                print(f"Output: {json.dumps(timeframe, indent=2)}")
            else:
                print(f"Unexpected result format: {result}")
        else:
            print(f"Could not parse: {result}")

if __name__ == "__main__":
    test_date_parser_integration()
