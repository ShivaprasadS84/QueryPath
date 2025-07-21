#!/usr/bin/env python3
"""
Test script for timeframe extraction in Patient Information Query Client
"""

import json
from patient_client import PatientInfoClient

def test_timeframe_extraction():
    """Test various timeframe patterns"""
    client = PatientInfoClient()
    
    test_cases = [
        # Basic timeframe patterns
        "Show me all female patients under 25 diagnosed with squamous cell carcinoma in the past two months",
        "Fetch cases of males over 50 diagnosed with prostate adenocarcinoma last year",
        "Give me all cases with lymphoma in females aged between 30 and 40 from the last six weeks",
        "Retrieve pathology reports for male patients diagnosed with melanoma during the first quarter of this year",
        "List cases from the past 10 days involving breast carcinoma in women above 45",
        "Get all male patients under 18 who were diagnosed with leukemia last month",
        "Find reports of colon adenocarcinoma in females aged 60 and above submitted in the last three days",
        "I want cases diagnosed with renal cell carcinoma in males in their 30s from the previous week",
        "Show all patients over 70, both male and female, with a diagnosis of non-Hodgkin's lymphoma within the last 90 days",
        "Pull up all female patients between 20 and 35 diagnosed with cervical dysplasia during June",
        
        # Advanced timeframe patterns
        "Display all pathology results for male patients with glioblastoma multiforme diagnosed in the last six months, regardless of age",
        "Provide a list of all female patients aged 55 to 65 with ovarian carcinoma diagnoses from the past year",
        "I need all cases of thyroid papillary carcinoma in females aged 20-40 diagnosed in the last two weeks",
        "Show me reports of pancreatic adenocarcinoma in male patients aged 40-60 from the current quarter",
        "List all diagnoses of chronic lymphocytic leukemia in male patients over 65 from the last 90 days",
        "Find all instances of endometrial hyperplasia in females over 45 reported in the last five days",
        "Get me all cases of hepatocellular carcinoma in male patients over 50 from the previous two months",
        "Display all reports of acute myeloid leukemia in children (under 12) of either gender from the last quarter",
        
        # Specific date patterns
        "Show cases diagnosed on 12th of July last year",
        "Find reports from yesterday",
        "Get cases from today",
        "List diagnoses from 2 weeks ago",
        "Show reports from 6 months ago",
        
        # No timeframe cases
        "Show me all female patients under 25 diagnosed with squamous cell carcinoma",
        "Find male patients over 65 with diabetes",
        "Patients between 30 and 50 years old",
    ]
    
    print("Testing Timeframe Extraction in Patient Information Query Client")
    print("=" * 80)
    print(f"Total test cases: {len(test_cases)}")
    
    successful_parses = 0
    failed_parses = 0
    
    for i, query in enumerate(test_cases, 1):
        print(f"\nTest {i}: {query}")
        print("-" * 80)
        
        # Get LLM result
        result = client.parse_query(query)
        
        if result:
            print(f"Result: {json.dumps(result, indent=2)}")
            
            # Basic structure validation
            required_keys = ["gender", "age", "diagnosis", "timeframe"]
            if all(key in result for key in required_keys):
                print("✅ Structure validation passed")
                
                # Check timeframe extraction
                timeframe = result.get("timeframe")
                if timeframe is not None:
                    print(f"✅ Timeframe extracted: '{timeframe}'")
                else:
                    print("ℹ️  No timeframe found (expected for some queries)")
                
                successful_parses += 1
            else:
                print("❌ Structure validation failed - missing keys")
                missing_keys = [key for key in required_keys if key not in result]
                print(f"Missing keys: {missing_keys}")
                failed_parses += 1
        else:
            print("❌ Failed to parse query")
            failed_parses += 1
        
        print()
    
    print("=" * 80)
    print("FINAL SUMMARY:")
    print(f"  Successful parses: {successful_parses}")
    print(f"  Failed parses: {failed_parses}")
    print(f"  Total tests: {len(test_cases)}")
    print(f"  Success rate: {(successful_parses/len(test_cases)*100):.1f}%")

if __name__ == "__main__":
    test_timeframe_extraction()
