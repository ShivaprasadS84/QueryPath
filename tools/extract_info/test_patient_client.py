#!/usr/bin/env python3
"""
Test script for Patient Information Query Client
"""

import json
from patient_client import PatientInfoClient

def analyze_query_expectations(query):
    """Analyze a query and return expected gender, age, and diagnosis"""
    query_lower = query.lower()
    
    # Gender analysis
    expected_gender = None
    if "both male and female" in query_lower or "both genders" in query_lower or "either gender" in query_lower:
        expected_gender = None
    elif "regardless of gender" in query_lower or "any gender" in query_lower:
        expected_gender = None
    elif "of any age or gender" in query_lower:
        expected_gender = None
    elif any(word in query_lower for word in ['female', 'women', 'woman']):
        expected_gender = "female"
    elif any(word in query_lower for word in ['male', 'men', 'man']):
        expected_gender = "male"
    
    # Age analysis
    expected_age = None
    if "under 12" in query_lower or "children (under 12)" in query_lower:
        expected_age = {"type": "max", "max": 12}
    elif "under 15" in query_lower or "children (under 15)" in query_lower:
        expected_age = {"type": "max", "max": 15}
    elif "under 18" in query_lower:
        expected_age = {"type": "max", "max": 18}
    elif "under 20" in query_lower:
        expected_age = {"type": "max", "max": 20}
    elif "under 25" in query_lower:
        expected_age = {"type": "max", "max": 25}
    elif "under 30" in query_lower:
        expected_age = {"type": "max", "max": 30}
    elif "over 70" in query_lower:
        expected_age = {"type": "min", "min": 70}
    elif "over 65" in query_lower:
        expected_age = {"type": "min", "min": 65}
    elif "over 60" in query_lower:
        expected_age = {"type": "min", "min": 60}
    elif "over 55" in query_lower:
        expected_age = {"type": "min", "min": 55}
    elif "over 50" in query_lower:
        expected_age = {"type": "min", "min": 50}
    elif "over 45" in query_lower:
        expected_age = {"type": "min", "min": 45}
    elif "over 40" in query_lower:
        expected_age = {"type": "min", "min": 40}
    elif "above 45" in query_lower:
        expected_age = {"type": "min", "min": 45}
    elif "aged 60 and above" in query_lower:
        expected_age = {"type": "min", "min": 60}
    elif "between 20 and 35" in query_lower:
        expected_age = {"type": "range", "min": 20, "max": 35}
    elif "between 30 and 40" in query_lower:
        expected_age = {"type": "range", "min": 30, "max": 40}
    elif "aged 55 to 65" in query_lower:
        expected_age = {"type": "range", "min": 55, "max": 65}
    elif "aged 20-40" in query_lower:
        expected_age = {"type": "range", "min": 20, "max": 40}
    elif "aged 40-60" in query_lower:
        expected_age = {"type": "range", "min": 40, "max": 60}
    elif "aged 25-45" in query_lower:
        expected_age = {"type": "range", "min": 25, "max": 45}
    elif "aged 18-25" in query_lower:
        expected_age = {"type": "range", "min": 18, "max": 25}
    elif "between 40 and 60" in query_lower:
        expected_age = {"type": "range", "min": 40, "max": 60}
    elif "aged 20-40" in query_lower:
        expected_age = {"type": "range", "min": 20, "max": 40}
    elif "aged 10-30" in query_lower:
        expected_age = {"type": "range", "min": 10, "max": 30}
    elif "aged 30-50" in query_lower:
        expected_age = {"type": "range", "min": 30, "max": 50}
    elif "in their 30s" in query_lower:
        expected_age = {"type": "range", "min": 30, "max": 39}
    elif "regardless of age" in query_lower:
        expected_age = None
    elif "of any age or gender" in query_lower:
        expected_age = None
    elif "any age" in query_lower:
        expected_age = None
    
    # Diagnosis analysis - extract key medical terms
    expected_diagnosis = None
    diagnoses = [
        "squamous cell carcinoma", "prostate adenocarcinoma", "lymphoma", "melanoma", 
        "breast carcinoma", "leukemia", "colon adenocarcinoma", "renal cell carcinoma",
        "non-hodgkin's lymphoma", "cervical dysplasia", "glioblastoma multiforme", 
        "ovarian carcinoma", "basal cell carcinoma", "thyroid papillary carcinoma",
        "pancreatic adenocarcinoma", "chronic lymphocytic leukemia", "endometrial hyperplasia",
        "hepatocellular carcinoma", "acute myeloid leukemia", "fibroadenoma",
        "testicular germ cell tumors", "pulmonary adenocarcinoma", "squamous cell carcinoma of the lung",
        "multiple myeloma", "benign prostatic hyperplasia", "inflammatory bowel disease",
        "atypical ductal hyperplasia", "hodgkin lymphoma", "actinic keratosis",
        "high-grade serous carcinoma of the ovary", "soft tissue sarcoma", "gastric adenocarcinoma",
        "uterine leiomyomas", "bladder transitional cell carcinoma", "acute lymphoblastic leukemia",
        "lobular carcinoma in situ", "oncocytoma", "esophageal adenocarcinoma",
        "primary peritoneal carcinoma", "salivary gland mucoepidermoid carcinoma", "rhabdomyosarcoma",
        "meningioma", "seminoma", "prostatic intraepithelial neoplasia", "vulvar squamous cell carcinoma",
        "neuroendocrine tumors of the lung", "follicular lymphoma", "gestational trophoblastic disease",
        "medulloblastoma", "ductal carcinoma in situ"
    ]
    
    for diagnosis in diagnoses:
        if diagnosis in query_lower:
            expected_diagnosis = diagnosis
            break
    
    # Handle special cases
    if "pin" in query_lower and "prostatic" in query_lower:
        expected_diagnosis = "prostatic intraepithelial neoplasia"
    elif "dcis" in query_lower:
        expected_diagnosis = "ductal carcinoma in situ"
    elif "crohn's or ulcerative colitis" in query_lower:
        expected_diagnosis = "inflammatory bowel disease"
    
    return {
        "gender": expected_gender,
        "age": expected_age,
        "diagnosis": expected_diagnosis
    }

def validate_result(expected, actual):
    """Validate actual result against expected values"""
    errors = []
    
    # Validate gender
    if expected["gender"] != actual.get("gender"):
        errors.append(f"Gender: expected {expected['gender']}, got {actual.get('gender')}")
    
    # Validate age
    expected_age = expected["age"]
    actual_age = actual.get("age")
    
    if expected_age is None and actual_age is not None:
        errors.append(f"Age: expected None, got {actual_age}")
    elif expected_age is not None and actual_age is None:
        errors.append(f"Age: expected {expected_age}, got None")
    elif expected_age is not None and actual_age is not None:
        if expected_age.get("type") != actual_age.get("type"):
            errors.append(f"Age type: expected {expected_age.get('type')}, got {actual_age.get('type')}")
        
        if expected_age.get("type") == "min" and expected_age.get("min") != actual_age.get("min"):
            errors.append(f"Age min: expected {expected_age.get('min')}, got {actual_age.get('min')}")
        elif expected_age.get("type") == "max" and expected_age.get("max") != actual_age.get("max"):
            errors.append(f"Age max: expected {expected_age.get('max')}, got {actual_age.get('max')}")
        elif expected_age.get("type") == "range":
            if expected_age.get("min") != actual_age.get("min"):
                errors.append(f"Age range min: expected {expected_age.get('min')}, got {actual_age.get('min')}")
            if expected_age.get("max") != actual_age.get("max"):
                errors.append(f"Age range max: expected {expected_age.get('max')}, got {actual_age.get('max')}")
        elif expected_age.get("type") == "exact" and expected_age.get("value") != actual_age.get("value"):
            errors.append(f"Age value: expected {expected_age.get('value')}, got {actual_age.get('value')}")
    
    # Validate diagnosis - check if expected diagnosis exists in actual diagnosis
    expected_diagnosis = expected["diagnosis"]
    actual_diagnosis = actual.get("diagnosis")
    
    if expected_diagnosis is None and actual_diagnosis is not None:
        errors.append(f"Diagnosis: expected None, got '{actual_diagnosis}'")
    elif expected_diagnosis is not None and actual_diagnosis is None:
        errors.append(f"Diagnosis: expected '{expected_diagnosis}', got None")
    elif expected_diagnosis is not None and actual_diagnosis is not None:
        # Check if expected diagnosis is contained in actual diagnosis (case-insensitive)
        if expected_diagnosis.lower() not in actual_diagnosis.lower():
            errors.append(f"Diagnosis: expected '{expected_diagnosis}' to be found in '{actual_diagnosis}'")
    
    return errors

def test_queries():
    """Test various patient query patterns with robust validation"""
    client = PatientInfoClient()
    
    test_cases = [
        "Show me all female patients under 25 diagnosed with squamous cell carcinoma in the past two months.",
        "Fetch cases of males over 50 diagnosed with prostate adenocarcinoma last year.",
        "Give me all cases with lymphoma in females aged between 30 and 40 from the last six weeks.",
        "Retrieve pathology reports for male patients diagnosed with melanoma during the first quarter of this year.",
        "List cases from the past 10 days involving breast carcinoma in women above 45.",
        "Get all male patients under 18 who were diagnosed with leukemia last month.",
        "Find reports of colon adenocarcinoma in females aged 60 and above submitted in the last three days.",
        "I want cases diagnosed with renal cell carcinoma in males in their 30s from the previous week.",
        "Show all patients over 70, both male and female, with a diagnosis of non-Hodgkin's lymphoma within the last 90 days.",
        "Pull up all female patients between 20 and 35 diagnosed with cervical dysplasia during June.",
        "Display all pathology results for male patients with glioblastoma multiforme diagnosed in the last six months, regardless of age.",
        "Provide a list of all female patients aged 55 to 65 with ovarian carcinoma diagnoses from the past year.",
        "Retrieve all biopsies showing basal cell carcinoma in patients of any gender under 30 within the last month.",
        "I need all cases of thyroid papillary carcinoma in females aged 20-40 diagnosed in the last two weeks.",
        "Show me reports of pancreatic adenocarcinoma in male patients aged 40-60 from the current quarter.",
        "List all diagnoses of chronic lymphocytic leukemia in male patients over 65 from the last 90 days.",
        "Find all instances of endometrial hyperplasia in females over 45 reported in the last five days.",
        "Get me all cases of hepatocellular carcinoma in male patients over 50 from the previous two months.",
        "Display all reports of acute myeloid leukemia in children (under 12) of either gender from the last quarter.",
        "Pull up all female patients aged 25-45 with fibroadenoma diagnoses from the last six months.",
        "Show all male patients aged 18-25 diagnosed with testicular germ cell tumors in the last year.",
        "Retrieve all pathology reports for patients over 70, both genders, with pulmonary adenocarcinoma diagnosed in the past 180 days.",
        "List cases of squamous cell carcinoma of the lung in males over 50 from the last three months.",
        "Find all diagnoses of multiple myeloma in patients over 60, regardless of gender, from the last year.",
        "Get me reports of benign prostatic hyperplasia in males over 40 from the last month.",
        "Display all cases of inflammatory bowel disease (Crohn's or Ulcerative Colitis) in patients under 30, both genders, from the past six weeks.",
        "Show all female patients with atypical ductal hyperplasia diagnosed in the last three months, regardless of age.",
        "Pull up all male patients under 30 diagnosed with Hodgkin lymphoma within the last year.",
        "Retrieve all biopsy results for skin lesions showing actinic keratosis in patients over 50 from the last two months.",
        "I want cases of high-grade serous carcinoma of the ovary in females over 50 from the previous six weeks.",
        "List all diagnoses of soft tissue sarcoma in patients aged 10-30, both genders, from the last 90 days.",
        "Find reports of gastric adenocarcinoma in male patients over 55 submitted in the last month.",
        "Get all female patients aged 30-50 diagnosed with uterine leiomyomas in the last year.",
        "Show all male patients over 60 with bladder transitional cell carcinoma diagnosed in the last six months.",
        "Display all cases of acute lymphoblastic leukemia in children (under 15) from the last quarter, regardless of gender.",
        "Pull up all female patients between 40 and 60 diagnosed with lobular carcinoma in situ from the previous year.",
        "Retrieve all pathology reports for male patients with renal masses showing oncocytoma in the last two months.",
        "List cases of esophageal adenocarcinoma in males over 40 from the last 90 days.",
        "Find all diagnoses of primary peritoneal carcinoma in females over 60 from the last year.",
        "Get me reports of salivary gland mucoepidermoid carcinoma in patients of any age or gender from the last six months.",
        "Show all female patients under 20 diagnosed with rhabdomyosarcoma in the last year.",
        "Display all cases of meningioma in female patients over 50 from the last two years.",
        "Pull up all male patients aged 20-40 with seminoma diagnoses from the last six months.",
        "Retrieve all prostate biopsies showing prostatic intraepithelial neoplasia (PIN) in males over 50 from the previous month.",
        "I want cases of vulvar squamous cell carcinoma in females over 60 from the last 90 days.",
        "List all diagnoses of neuroendocrine tumors of the lung in patients over 40, both genders, from the last year.",
        "Find reports of follicular lymphoma in patients over 50, regardless of gender, submitted in the last six months.",
        "Get all female patients aged 25-45 diagnosed with gestational trophoblastic disease in the last year.",
        "Show all male patients under 15 with medulloblastoma diagnoses from the last two years.",
        "Display all cases of ductal carcinoma in situ (DCIS) in female patients over 40 from the last 90 days."
    ]
    
    print("Testing Patient Information Query Client with Robust Validation")
    print("=" * 80)
    print(f"Total test cases: {len(test_cases)}")
    
    successful_parses = 0
    failed_parses = 0
    validation_errors = 0
    
    for i, query in enumerate(test_cases, 1):
        print(f"\nTest {i}: {query}")
        print("-" * 80)
        
        # Analyze expected values
        expected = analyze_query_expectations(query)
        print(f"Expected: {json.dumps(expected, indent=2)}")
        
        # Get LLM result
        result = client.parse_query(query)
        
        if result:
            print(f"Actual: {json.dumps(result, indent=2)}")
            
            # Basic structure validation
            required_keys = ["gender", "age", "diagnosis"]
            if all(key in result for key in required_keys):
                print("✅ Structure validation passed")
                
                # Detailed validation against expectations
                errors = validate_result(expected, result)
                if not errors:
                    print("✅ Content validation passed")
                    successful_parses += 1
                else:
                    print("❌ Content validation failed:")
                    for error in errors:
                        print(f"  - {error}")
                    validation_errors += 1
            else:
                print("❌ Structure validation failed - missing keys")
                failed_parses += 1
        else:
            print("❌ Failed to parse query")
            failed_parses += 1
        
        print()
    
    print("=" * 80)
    print("FINAL SUMMARY:")
    print(f"  Perfect matches: {successful_parses}")
    print(f"  Validation errors: {validation_errors}")
    print(f"  Parse failures: {failed_parses}")
    print(f"  Total tests: {len(test_cases)}")
    print(f"  Perfect success rate: {(successful_parses/len(test_cases)*100):.1f}%")
    print(f"  Parse success rate: {((successful_parses + validation_errors)/len(test_cases)*100):.1f}%")

if __name__ == "__main__":
    test_queries()
