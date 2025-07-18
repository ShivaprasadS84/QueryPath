# Import the OpenAI client library instead of llama_cpp
from openai import OpenAI
import json
import re
from datetime import datetime
import time
from llama_cpp import LlamaGrammar

# Initialize the OpenAI client to connect to your local server
# The server exposes an OpenAI-compatible API, so we use the OpenAI client.
# The base_url should point to the /v1 endpoint of your server.
client = OpenAI(
    base_url="http://localhost:8080/v1",
    api_key="not-needed"  # API key is not required for local server but the field is mandatory
)

# The GBNF grammar string remains the same.
# We no longer need to compile it with LlamaGrammar.
pathology_grammar = r'''
root ::= object
value ::= object | array | string | number | boolean | null
object ::= "{" ws ( string ":" ws value ( "," ws string ":" ws value )* )? "}" ws
array ::= "[" ws ( value ( "," ws value )* )? "]" ws
string ::= "\"" ( [^"\\] | "\\" ( ["\\/bfnrt] | "u" [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F] ) )* "\"" ws
number ::= ( "-" )? ( "0" | [1-9] [0-9]* ) ( "." [0-9]+ )? ( [eE] [+-]? [0-9]+ )? ws
boolean ::= "true" | "false"
null ::= "null"
ws ::= [ \t\n]*
'''

class PathologyQueryParser:
    def __init__(self):
        self.current_date = datetime.now()
        self.last_response_time = 0

    def get_system_prompt(self):
        return f"""You are a medical query parser. Your task is to parse natural language pathology queries and convert them to structured JSON according to the PathologyQuery schema.

Current date: {self.current_date.strftime('%Y-%m-%d')} ({self.current_date.strftime('%A')})

Schema requirements:
1. gender: Array of "male" and/or "female"
2. age: Object with minimumAge and/or maximumAge (inclusive bounds)
3. diagnosis: Full diagnosis string
4. diseaseCategory: High-level category (optional)
5. timePeriod: One of three types:
   - relative: {{"type": "relative", "value": number, "unit": "day/week/month/year", "qualifier": "last/past/previous"}}
   - absolute: {{"type": "absolute", "startDate": "YYYY-MM-DD", "endDate": "YYYY-MM-DD"}}
   - quarter: {{"type": "quarter", "quarter": 1-4, "year": YYYY}}

Parsing rules:
- "under X" = maximumAge: X-1
- "over X" = minimumAge: X+1
- "between X and Y" = minimumAge: X, maximumAge: Y
- "in their Xs" = minimumAge: X0, maximumAge: X9 (e.g., "30s" = 30-39)
- "last/past X days/weeks/months/years" = relative period
- Specific months/quarters = absolute or quarter periods
- "both male and female" = ["male", "female"]

Extract disease categories when possible (carcinoma, lymphoma, adenocarcinoma, etc.)"""

    def parse_query(self, query):
        system_prompt = self.get_system_prompt()

        # The user query is now separated from the system prompt
        user_prompt = f"""Query: "{query}"

Parse this query and output ONLY valid JSON according to the PathologyQuery schema:
"""
        # The API call is changed to client.chat.completions.create
        start_time = time.time()
        response = client.chat.completions.create(
            # The model name can often be a placeholder when only one model is served.
            model="local-model",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=500,
            temperature=0.1,
            stop=["\n\n", "```"],
            extra_body={
                "grammar": pathology_grammar
            }
        )
        end_time = time.time()

        self.last_response_time = end_time - start_time
        print(f"[REST API] LLM Response Time: {self.last_response_time:.4f} seconds")

        return response.choices[0].message.content

    def validate_and_parse(self, query):
        """Parse query and validate the JSON output"""
        total_start_time = time.time()
        try:
            json_output = self.parse_query(query)
            cleaned_json = re.sub(r'```json\n|```', '', json_output).strip()
            parsed_json = json.loads(cleaned_json)

            required_fields = ['gender', 'diagnosis', 'timePeriod']
            for field in required_fields:
                if field not in parsed_json:
                    raise ValueError(f"Missing required field: {field}")

            total_end_time = time.time()
            total_time = total_end_time - total_start_time
            print(f"[REST API] Total Processing Time: {total_time:.4f} seconds")
            print(f"[REST API] Overhead Time: {total_time - self.last_response_time:.4f} seconds")

            return parsed_json, None
        except json.JSONDecodeError as e:
            return None, f"JSON parsing error: {e}\nRaw output from model: {json_output}"
        except Exception as e:
            return None, f"Validation error: {e}"

if __name__ == '__main__':
    parser = PathologyQueryParser()
    while True:
        result, error = parser.validate_and_parse(input("Query: "))

        if error:
            print(f"An error occurred: {error}")
        else:
            print(json.dumps(result, indent=2))