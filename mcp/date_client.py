import asyncio
import json
import time
import os
from datetime import datetime
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8080/v1",
    api_key="not-needed"
)

def load_grammar():
    """Load GBNF grammar for structured output"""
    grammar_file = os.path.join(os.path.dirname(__file__), "date_query.gbnf")
    try:
        with open(grammar_file, 'r') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Warning: Grammar file {grammar_file} not found")
        return ""

grammar = load_grammar()

async def process_query(session, user_query: str) -> dict:
    """Process user query using LLM and MCP server"""
    
    system_prompt = f"""You are a date query parser. Convert natural language date queries into structured JSON.

Current date: {datetime.now().strftime('%Y-%m-%d')} ({datetime.now().strftime('%A')})

RULES:
1. For single dates (today, yesterday, 3 days ago, last Thursday, 3rd of this month): use "single_date"
2. For date ranges (last week, this week, last month, jan to march): use "date_range"
3. For "Nth of [this/last] month" patterns: use "specific_day_of_month" reference point
4. WEEKS and MONTHS: "2 weeks ago", "1 month ago" are SINGLE dates, not ranges
5. WEEK RANGES: "this week", "last week" are RANGES (Monday to Sunday)
6. CRITICAL: Any query mentioning "today" (including "cases today", "what happened today") = SINGLE DATE

REFERENCE POINTS:
- "today" - current date (use for "X days/weeks/months ago")
- "start_of_week" - start of week (Monday) - use for week ranges
- "start_of_month" - start of month - use for month ranges
- "specific_month" - for month names (offset_unit = month name)
- "specific_weekday" - for weekdays (offset_unit = weekday name)
- "specific_day_of_month" - for specific day numbers (offset_unit = day number)

EXAMPLES:

# Basic relative dates (SINGLE dates):
"today" → {{"query_type": "single_date", "parameters": {{"reference_point": "today", "offset_value": 0, "offset_unit": "days"}}}}
"yesterday" → {{"query_type": "single_date", "parameters": {{"reference_point": "today", "offset_value": -1, "offset_unit": "days"}}}}
"3 days ago" → {{"query_type": "single_date", "parameters": {{"reference_point": "today", "offset_value": -3, "offset_unit": "days"}}}}
"2 weeks ago" → {{"query_type": "single_date", "parameters": {{"reference_point": "today", "offset_value": -2, "offset_unit": "weeks"}}}}
"1 month ago" → {{"query_type": "single_date", "parameters": {{"reference_point": "today", "offset_value": -1, "offset_unit": "months"}}}}

# Weekdays (SINGLE dates):
"last Thursday" → {{"query_type": "single_date", "parameters": {{"reference_point": "specific_weekday", "offset_value": -1, "offset_unit": "thursday"}}}}
"last Monday" → {{"query_type": "single_date", "parameters": {{"reference_point": "specific_weekday", "offset_value": -1, "offset_unit": "monday"}}}}
"last Tuesday" → {{"query_type": "single_date", "parameters": {{"reference_point": "specific_weekday", "offset_value": -1, "offset_unit": "tuesday"}}}}

# SPECIFIC DAYS OF MONTH (SINGLE dates):
"3rd of this month" → {{"query_type": "single_date", "parameters": {{"reference_point": "specific_day_of_month", "offset_value": 0, "offset_unit": "3"}}}}
"15th of last month" → {{"query_type": "single_date", "parameters": {{"reference_point": "specific_day_of_month", "offset_value": -1, "offset_unit": "15"}}}}
"1st of next month" → {{"query_type": "single_date", "parameters": {{"reference_point": "specific_day_of_month", "offset_value": 1, "offset_unit": "1"}}}}

# Date ranges (RANGES):
"this week" → {{"query_type": "date_range", "parameters": {{"start_reference": "start_of_week", "start_offset_value": 0, "start_offset_unit": "weeks", "end_reference": "start_of_week", "end_offset_value": 0, "end_offset_unit": "weeks"}}}}
"last week" → {{"query_type": "date_range", "parameters": {{"start_reference": "start_of_week", "start_offset_value": -1, "start_offset_unit": "weeks", "end_reference": "start_of_week", "end_offset_value": -1, "end_offset_unit": "weeks"}}}}
"last month" → {{"query_type": "date_range", "parameters": {{"start_reference": "start_of_month", "start_offset_value": -1, "start_offset_unit": "months", "end_reference": "start_of_month", "end_offset_value": -1, "end_offset_unit": "months"}}}}
"feb" → {{"query_type": "date_range", "parameters": {{"start_reference": "specific_month", "start_offset_value": 0, "start_offset_unit": "february", "end_reference": "specific_month", "end_offset_value": 0, "end_offset_unit": "february"}}}}
"march last year" → {{"query_type": "date_range", "parameters": {{"start_reference": "specific_month", "start_offset_value": -1, "start_offset_unit": "march", "end_reference": "specific_month", "end_offset_value": -1, "end_offset_unit": "march"}}}}
"march and april this year" → {{"query_type": "date_range", "parameters": {{"start_reference": "specific_month", "start_offset_value": 0, "start_offset_unit": "march", "end_reference": "specific_month", "end_offset_value": 0, "end_offset_unit": "april"}}}}
"jan to march this year" → {{"query_type": "date_range", "parameters": {{"start_reference": "specific_month", "start_offset_value": 0, "start_offset_unit": "january", "end_reference": "specific_month", "end_offset_value": 0, "end_offset_unit": "march"}}}}
"march to august last year" → {{"query_type": "date_range", "parameters": {{"start_reference": "specific_month", "start_offset_value": -1, "start_offset_unit": "march", "end_reference": "specific_month", "end_offset_value": -1, "end_offset_unit": "august"}}}}

KEY DISTINCTIONS:
- "today" = single date (current day)
- "2 weeks ago" = single date (exactly 14 days ago)
- "last week" = date range (Monday to Sunday of last week)
- "1 month ago" = single date (same day last month)
- "last month" = date range (full month)

CRITICAL WEEKDAY PARSING RULES:
- "last Monday" = specific_weekday with offset_unit="monday" (NOT start_of_week!)
- "last Tuesday" = specific_weekday with offset_unit="tuesday" (NOT start_of_week!)
- "last Wednesday" = specific_weekday with offset_unit="wednesday" (NOT start_of_week!)
- "last Thursday" = specific_weekday with offset_unit="thursday" (NOT start_of_week!)
- "last Friday" = specific_weekday with offset_unit="friday" (NOT start_of_week!)
- "last Saturday" = specific_weekday with offset_unit="saturday" (NOT start_of_week!)
- "last Sunday" = specific_weekday with offset_unit="sunday" (NOT start_of_week!)

WRONG EXAMPLES (DO NOT DO THIS):
❌ "last Monday" → start_of_week with weeks (WRONG!)
❌ "last Tuesday" → start_of_week with weeks (WRONG!)

CORRECT EXAMPLES:
✅ "last Monday" → specific_weekday with offset_unit="monday"
✅ "last Tuesday" → specific_weekday with offset_unit="tuesday"

ONLY use start_of_week for:
- "last week" (full week range)
- "this week" (full week range)
- "next week" (full week range)

Parse the query and respond with JSON only."""

    start_time = time.time()
    
    try:
        response = client.chat.completions.create(
            model="local-model",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            temperature=0.0,
            max_tokens=300,
            extra_body={"grammar": grammar} if grammar else {}
        )
    except Exception as e:
        print(f"Grammar failed, trying without: {e}")
        response = client.chat.completions.create(
            model="local-model",
            messages=[
                {"role": "system", "content": system_prompt},
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
        parsed = json.loads(llm_response)
        query_type = parsed["query_type"]
        params = parsed["parameters"]
        
        if query_type == "single_date":
            result = await session.call_tool("get_single_date", params)
            date_result = result.content[0].text
            return {"type": "single_date", "date": date_result}
            
        elif query_type == "date_range":
            if (params["start_reference"] == "start_of_week" and 
                params["end_reference"] == "start_of_week" and
                params["start_offset_value"] == params["end_offset_value"]):
                week_params = {
                    "week_offset": params["start_offset_value"]
                }
                result = await session.call_tool("get_week_range", week_params)
            
            elif (params["start_reference"] == "specific_month" and 
                  params["end_reference"] == "specific_month" and
                  params["start_offset_unit"] == params["end_offset_unit"]):
                month_params = {
                    "month_name": params["start_offset_unit"],
                    "year_offset": params["start_offset_value"]
                }
                result = await session.call_tool("get_month_range", month_params)
            
            else:
                result = await session.call_tool("get_date_range", params)
            
            range_result = json.loads(result.content[0].text)
            return {"type": "date_range", **range_result}
        
        else:
            return {"error": f"Unknown query type: {query_type}"}
    
    except Exception as e:
        print(f"Error processing query: {e}")
        return {"error": str(e)}

async def run_client():
    """Run the interactive client"""
    server_params = StdioServerParameters(
        command="python", args=["server.py"], cwd=os.path.dirname(__file__)
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            print("=== Simple DateTime Query System ===")
            print("Enter date queries (type 'quit' to exit)")
            print("\nExamples:")
            print("- get me cases from yesterday")
            print("- get me cases from last week")
            print("- get me cases from feb")
            print("- get me cases from march last year")
            print()
            
            while True:
                try:
                    query = input("Query: ").strip()
                    if query.lower() in ['quit', 'exit', 'q']:
                        break
                    
                    if query:
                        print(f"\nProcessing: {query}")
                        result = await process_query(session, query)
                        
                        print("Result:")
                        print(json.dumps(result, indent=2))
                        print()
                
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(run_client())
