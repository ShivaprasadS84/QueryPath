#!/usr/bin/env python3
"""
Patient Information Query Client
Extracts structured patient information from natural language queries using LLM
"""

import json
import os
import time
from openai import OpenAI

def load_grammar():
    """Load GBNF grammar for structured output"""
    grammar_file = os.path.join(os.path.dirname(__file__), "grammar.gbnf")
    try:
        with open(grammar_file, 'r') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Warning: Grammar file {grammar_file} not found")
        return ""

def get_system_prompt():
    """System prompt for patient information extraction"""
    return """You are a medical query parser that extracts structured patient information from natural language queries.

Your task is to parse patient queries and return ONLY valid JSON with the following EXACT structure:

{
  "gender": "male" | "female" | null,
  "age": {
    "type": "exact" | "range" | "min" | "max",
    "value": number,
    "min": number,
    "max": number
  } | null,
  "diagnosis": "condition name" | null
}

IMPORTANT JSON RULES:
- If age is not specified or "any age", use: "age": null
- If gender is not specified or "any gender", use: "gender": null
- NEVER use "type": "any" - this is invalid
- NEVER repeat fields like "min": null multiple times
- Each field should appear exactly once

CRITICAL PARSING RULES:

1. Gender Rules:
   - "male", "men" → "male"
   - "female", "women", "woman" → "female"  
   - "both male and female", "both genders", "either gender", "regardless of gender" → null
   - If no gender mentioned → null

2. Age Rules (IGNORE TIME PERIODS):
   - "under X", "children (under X)" → {"type": "max", "max": X}
   - "over X", "above X", "X and above" → {"type": "min", "min": X}
   - "between X and Y", "aged X to Y", "aged X-Y" → {"type": "range", "min": X, "max": Y}
   - "X years old" → {"type": "exact", "value": X}
   - "in their Xs" (e.g., "in their 30s") → {"type": "range", "min": X0, "max": X9}
   - "any age", "regardless of age", "of any age" → null
   - If no age mentioned → null
   - CRITICAL: DO NOT confuse time periods ("last 2 months", "first quarter") with age
   - CRITICAL: "under X" means maximum age X, NOT minimum

3. Diagnosis Rules:
   - Extract the main medical condition mentioned
   - Ignore time-related phrases ("last year", "past months", etc.)
   - Focus on the actual disease/condition name

4. Time Period Rules:
   - COMPLETELY IGNORE all time references ("last year", "past 2 months", "first quarter", "in the last two months", etc.)
   - These are NOT age constraints - they are time periods for when reports were submitted
   - "in the last two months" does NOT mean age under 2 - it means reports from 2 months ago
   - "last year" does NOT mean age under 1 - it means reports from last year
   - Only extract patient age, gender, and diagnosis - IGNORE when reports were submitted

EXAMPLES:
Query: "Show me all female patients under 25 diagnosed with squamous cell carcinoma"
Output: {"gender": "female", "age": {"type": "max", "max": 25}, "diagnosis": "squamous cell carcinoma"}

Query: "Find male patients over 65 with diabetes"
Output: {"gender": "male", "age": {"type": "min", "min": 65}, "diagnosis": "diabetes"}

Query: "Patients between 30 and 50 years old"
Output: {"gender": null, "age": {"type": "range", "min": 30, "max": 50}, "diagnosis": null}

Query: "Find reports of colon adenocarcinoma in females aged 60 and above"
Output: {"gender": "female", "age": {"type": "min", "min": 60}, "diagnosis": "colon adenocarcinoma"}

Query: "List diagnoses in patients over 40, both genders"
Output: {"gender": null, "age": {"type": "min", "min": 40}, "diagnosis": null}

Query: "Cases in males in their 30s"
Output: {"gender": "male", "age": {"type": "range", "min": 30, "max": 39}, "diagnosis": null}

Query: "Get me reports of salivary gland mucoepidermoid carcinoma in patients of any age or gender from the last six months"
Output: {"gender": null, "age": null, "diagnosis": "salivary gland mucoepidermoid carcinoma"}

Query: "Reports in patients of any age or gender"
Output: {"gender": null, "age": null, "diagnosis": null}

Query: "Retrieve pathology reports for male patients diagnosed with melanoma during the first quarter of this year"
Output: {"gender": "male", "age": null, "diagnosis": "melanoma"}

Query: "Display all cases of acute lymphoblastic leukemia in children (under 15) from the last quarter, regardless of gender"
Output: {"gender": null, "age": {"type": "max", "max": 15}, "diagnosis": "acute lymphoblastic leukemia"}

Query: "Show all patients over 70, both male and female, with a diagnosis of non-Hodgkin's lymphoma within the last 90 days"
Output: {"gender": null, "age": {"type": "min", "min": 70}, "diagnosis": "non-Hodgkin's lymphoma"}

Query: "Retrieve all biopsy results for skin lesions showing actinic keratosis in patients over 50 from the last two months"
Output: {"gender": null, "age": {"type": "min", "min": 50}, "diagnosis": "actinic keratosis"}

Query: "Fetch cases of males over 50 diagnosed with prostate adenocarcinoma last year"
Output: {"gender": "male", "age": {"type": "min", "min": 50}, "diagnosis": "prostate adenocarcinoma"}

Query: "Retrieve all pathology reports for male patients with renal masses showing oncocytoma in the last two months"
Output: {"gender": "male", "age": null, "diagnosis": "oncocytoma"}

CRITICAL REMINDERS:
- "any age" = "age": null (NOT {"type": "any"})
- "any gender" = "gender": null
- "both genders" = "gender": null
- "under X" = {"type": "max", "max": X} (maximum age)
- "over X" = {"type": "min", "min": X} (minimum age)
- CRITICAL: "over 50" means AT LEAST 50 years old = {"type": "min", "min": 50}
- CRITICAL: "under 50" means AT MOST 50 years old = {"type": "max", "max": 50}
- IGNORE time periods like "last 2 months", "first quarter", "last year", "in the last two months"
- CRITICAL: "in the last two months" is NOT age - it's when reports were submitted
- CRITICAL: Numbers in time phrases are NOT age constraints
- Return ONLY the JSON object, no explanations or additional text."""

class PatientInfoClient:
    def __init__(self):
        self.client = OpenAI(
            base_url="http://localhost:8080/v1",
            api_key="not-needed"
        )
        self.grammar = load_grammar()
        self.system_prompt = get_system_prompt()
    
    def parse_query(self, user_query):
        """Parse a natural language patient query into structured JSON"""
        print(f"Processing query: {user_query}")
        
        start_time = time.time()
        
        try:
            response = self.client.chat.completions.create(
                model="local-model",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_query}
                ],
                temperature=0.0,
                max_tokens=300,
                extra_body={"grammar": self.grammar} if self.grammar else {}
            )
        except Exception as e:
            print(f"Grammar failed, trying without: {e}")
            response = self.client.chat.completions.create(
                model="local-model",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_query}
                ],
                temperature=0.0,
                max_tokens=300
            )
        
        llm_time = time.time() - start_time
        print(f"LLM Response Time: {llm_time:.3f}s")
        
        llm_response = response.choices[0].message.content.strip()
        print(f"LLM parsed: {llm_response}")
        
        try:
            # Parse the JSON response
            parsed_json = json.loads(llm_response)
            return parsed_json
        except json.JSONDecodeError as e:
            print(f"JSON parsing failed: {e}")
            print(f"Raw response: {llm_response}")
            return None
    
    def interactive_mode(self):
        """Interactive mode for testing queries"""
        print("Patient Information Query Parser")
        print("Enter patient queries (or 'quit' to exit):")
        print("\nExample queries:")
        print("- Show me all female patients under 25 diagnosed with squamous cell carcinoma in the past two months")
        print("- Find male patients over 65 with diabetes")
        print("- Patients between 30 and 50 years old with hypertension")
        print("- Women diagnosed with breast cancer in the last year")
        print()
        
        while True:
            try:
                query = input("\nEnter query: ").strip()
                if query.lower() in ['quit', 'exit', 'q']:
                    break
                
                if not query:
                    continue
                
                result = self.parse_query(query)
                if result:
                    print(f"Structured output: {json.dumps(result, indent=2)}")
                else:
                    print("Failed to parse query")
                    
            except KeyboardInterrupt:
                break
        
        print("\nGoodbye!")

def main():
    """Main function for testing"""
    client = PatientInfoClient()
    
    # Test with the example query
    test_query = "Show me all female patients under 25 diagnosed with squamous cell carcinoma in the past two months."
    
    print("Testing with example query:")
    result = client.parse_query(test_query)
    
    if result:
        print(f"\nStructured output:")
        print(json.dumps(result, indent=2))
    
    # Start interactive mode
    print("\n" + "="*50)
    client.interactive_mode()

if __name__ == "__main__":
    main()
