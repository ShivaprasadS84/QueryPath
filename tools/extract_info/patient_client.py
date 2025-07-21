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
  "diagnosis": "condition name" | null,
  "timeframe": "temporal expression" | null
}

IMPORTANT JSON RULES:
- If age is not specified or "any age", use: "age": null
- If gender is not specified or "any gender", use: "gender": null
- If timeframe is not specified, use: "timeframe": null
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
   - Focus on the actual disease/condition name
   - Ignore time-related phrases when extracting diagnosis

4. Timeframe Rules:
   - Extract temporal expressions that indicate when cases/reports were submitted or occurred
   - Preserve the original phrasing as much as possible
   - Common patterns to recognize:
     * "past X days/weeks/months/years" → "past X days/weeks/months/years"
     * "last X days/weeks/months/years" → "last X days/weeks/months/years"
     * "previous X days/weeks/months/years" → "previous X days/weeks/months/years"
     * "in the past X days/weeks/months/years" → "past X days/weeks/months/years"
     * "in the last X days/weeks/months/years" → "last X days/weeks/months/years"
     * "from the past X days/weeks/months/years" → "past X days/weeks/months/years"
     * "from the last X days/weeks/months/years" → "last X days/weeks/months/years"
     * "within the last X days/weeks/months/years" → "last X days/weeks/months/years"
     * "during the last X days/weeks/months/years" → "last X days/weeks/months/years"
     * "X days/weeks/months/years ago" → "X days/weeks/months/years ago"
     * "yesterday" → "yesterday"
     * "today" → "today"
     * "last week" → "last week"
     * "last month" → "last month"
     * "last year" → "last year"
     * "this week" → "this week"
     * "this month" → "this month"
     * "this year" → "this year"
     * "current week/month/year/quarter" → "current week/month/year/quarter"
     * "first/second/third/fourth quarter" → "first/second/third/fourth quarter"
     * "last quarter" → "last quarter"
     * "previous quarter" → "previous quarter"
     * "Q1/Q2/Q3/Q4" → "Q1/Q2/Q3/Q4"
     * "first/second/third/fourth quarter of this year" → "first/second/third/fourth quarter"
     * "last Monday/Tuesday/Wednesday/Thursday/Friday/Saturday/Sunday" → "last Monday/Tuesday/etc."
     * "previous Monday/Tuesday/Wednesday/Thursday/Friday/Saturday/Sunday" → "previous Monday/Tuesday/etc."
     * Specific dates: "12th of July last year", "January 15th", "March 2024", etc.
     * Month names: "during June", "in March", "from February", etc.
   - If no timeframe is mentioned, use: "timeframe": null
   - CRITICAL: Do NOT confuse timeframes with age constraints
   - "past 2 months" is a timeframe, NOT an age of 2 months

EXAMPLES:
Query: "Show me all female patients under 25 diagnosed with squamous cell carcinoma"
Output: {"gender": "female", "age": {"type": "max", "max": 25}, "diagnosis": "squamous cell carcinoma", "timeframe": null}

Query: "Find male patients over 65 with diabetes"
Output: {"gender": "male", "age": {"type": "min", "min": 65}, "diagnosis": "diabetes", "timeframe": null}

Query: "Patients between 30 and 50 years old"
Output: {"gender": null, "age": {"type": "range", "min": 30, "max": 50}, "diagnosis": null, "timeframe": null}

Query: "Patients between 30 and 50 years old with hypertension"
Output: {"gender": null, "age": {"type": "range", "min": 30, "max": 50}, "diagnosis": "hypertension", "timeframe": null}

Query: "Find reports of colon adenocarcinoma in females aged 60 and above submitted in the last three days"
Output: {"gender": "female", "age": {"type": "min", "min": 60}, "diagnosis": "colon adenocarcinoma", "timeframe": "last three days"}

Query: "List diagnoses in patients over 40, both genders"
Output: {"gender": null, "age": {"type": "min", "min": 40}, "diagnosis": null, "timeframe": null}

Query: "Cases in males in their 30s from the previous week"
Output: {"gender": "male", "age": {"type": "range", "min": 30, "max": 39}, "diagnosis": null, "timeframe": "previous week"}

Query: "Get me reports of salivary gland mucoepidermoid carcinoma in patients of any age or gender from the last six months"
Output: {"gender": null, "age": null, "diagnosis": "salivary gland mucoepidermoid carcinoma", "timeframe": "last six months"}

Query: "Reports in patients of any age or gender"
Output: {"gender": null, "age": null, "diagnosis": null, "timeframe": null}

Query: "Retrieve pathology reports for male patients diagnosed with melanoma during the first quarter of this year"
Output: {"gender": "male", "age": null, "diagnosis": "melanoma", "timeframe": "first quarter"}

Query: "Display all cases of acute lymphoblastic leukemia in children (under 15) from the last quarter, regardless of gender"
Output: {"gender": null, "age": {"type": "max", "max": 15}, "diagnosis": "acute lymphoblastic leukemia", "timeframe": "last quarter"}

Query: "Show all patients over 70, both male and female, with a diagnosis of non-Hodgkin's lymphoma within the last 90 days"
Output: {"gender": null, "age": {"type": "min", "min": 70}, "diagnosis": "non-Hodgkin's lymphoma", "timeframe": "last 90 days"}

Query: "Retrieve all biopsy results for skin lesions showing actinic keratosis in patients over 50 from the last two months"
Output: {"gender": null, "age": {"type": "min", "min": 50}, "diagnosis": "actinic keratosis", "timeframe": "last two months"}

Query: "Fetch cases of males over 50 diagnosed with prostate adenocarcinoma last year"
Output: {"gender": "male", "age": {"type": "min", "min": 50}, "diagnosis": "prostate adenocarcinoma", "timeframe": "last year"}

Query: "Retrieve all pathology reports for male patients with renal masses showing oncocytoma in the last two months"
Output: {"gender": "male", "age": null, "diagnosis": "oncocytoma", "timeframe": "last two months"}

Query: "Show me all female patients under 25 diagnosed with squamous cell carcinoma in the past two months"
Output: {"gender": "female", "age": {"type": "max", "max": 25}, "diagnosis": "squamous cell carcinoma", "timeframe": "past two months"}

Query: "List cases from the past 10 days involving breast carcinoma in women above 45"
Output: {"gender": "female", "age": {"type": "min", "min": 45}, "diagnosis": "breast carcinoma", "timeframe": "past 10 days"}

Query: "Get all male patients under 18 who were diagnosed with leukemia last month"
Output: {"gender": "male", "age": {"type": "max", "max": 18}, "diagnosis": "leukemia", "timeframe": "last month"}

Query: "Pull up all female patients between 20 and 35 diagnosed with cervical dysplasia during June"
Output: {"gender": "female", "age": {"type": "range", "min": 20, "max": 35}, "diagnosis": "cervical dysplasia", "timeframe": "during June"}

Query: "I need all cases of thyroid papillary carcinoma in females aged 20-40 diagnosed in the last two weeks"
Output: {"gender": "female", "age": {"type": "range", "min": 20, "max": 40}, "diagnosis": "thyroid papillary carcinoma", "timeframe": "last two weeks"}

Query: "Show me reports of pancreatic adenocarcinoma in male patients aged 40-60 from the current quarter"
Output: {"gender": "male", "age": {"type": "range", "min": 40, "max": 60}, "diagnosis": "pancreatic adenocarcinoma", "timeframe": "current quarter"}

CRITICAL REMINDERS:
- "any age" = "age": null (NOT {"type": "any"})
- "any gender" = "gender": null
- "both genders" = "gender": null
- "under X" = {"type": "max", "max": X} (maximum age)
- "over X" = {"type": "min", "min": X} (minimum age)
- CRITICAL: "over 50" means AT LEAST 50 years old = {"type": "min", "min": 50}
- CRITICAL: "under 50" means AT MOST 50 years old = {"type": "max", "max": 50}
- EXTRACT timeframes like "last 2 months", "first quarter", "last year", "past two months"
- CRITICAL: "in the last two months" is a TIMEFRAME, NOT an age constraint
- CRITICAL: "past 2 months" goes in "timeframe": "past 2 months", NOT in age
- CRITICAL: Numbers in time phrases are timeframes, NOT age constraints
- If no timeframe mentioned: "timeframe": null
- Preserve original timeframe phrasing: "past two months", "last year", "10 days ago", etc.
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
