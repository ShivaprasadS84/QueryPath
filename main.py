from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import sys
import os

# Add tools directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'tools', 'extract_info'))

from models import SearchResponse
from patient_client import PatientInfoClient
from openai import OpenAI

query_path_app = FastAPI(title="Medical Query API", description="Unified medical query processing API")

# Initialize the patient info client (handles both LLM calls and embedding initialization)
patient_client = PatientInfoClient()

# Initialize both LLM clients for caching
print("🔄 Initializing LLM clients for caching...")

# Initialize patient info LLM (port 8080) with actual system prompt and medical query
try:
    # Use a sample medical query from strings.txt for proper initialization
    sample_query = "Fetch cases of males over 50 diagnosed with prostate adenocarcinoma last year."
    print(f"🔥 Warming up patient info LLM with: {sample_query}")
    
    # This will initialize the patient client's LLM with the actual system prompt
    warmup_result = patient_client.parse_query(sample_query)
    print(f"✅ Patient info LLM (port 8080) initialized and cached with actual system prompt")
    print(f"📋 Warmup result: {warmup_result}")
except Exception as e:
    print(f"⚠️ Could not initialize patient info LLM: {e}")

# Embedding LLM (port 8081) is already initialized by the patient_client RAG system
if patient_client.rag_system:
    print("✅ Embedding LLM (port 8081) initialized and cached via RAG system")
    print(f"🔍 RAG system using collection: {patient_client.rag_system.collection_name}")
else:
    print("⚠️ Embedding LLM (port 8081) not available - RAG system failed to initialize")

print("🚀 All LLM clients ready for fast subsequent calls")

origins = [
    "https://localhost:4200",
]

query_path_app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@query_path_app.get("/search", response_model=SearchResponse)
async def search(q: str = Query(..., description="Medical query to process")):
    """
    Process a medical query and extract temporal and patient information.
    
    Example queries:
    - "Fetch cases of males over 50 diagnosed with prostate adenocarcinoma last year"
    - "Show me cases from last week for female patients with diabetes"
    - "Find cases from yesterday for patients over 65"
    """
    try:
        print(f"🔍 Processing query: {q}")
        
        # Process the medical query using the patient client
        result = patient_client.parse_query(q)
        
        # Debug: Print the raw result
        print(f"📋 Patient client result: {result}")
        
        # The result already matches our SearchResponse model structure
        if result:
            return SearchResponse(**result)
        else:
            # Return empty response if no result
            return SearchResponse()
        
    except Exception as e:
        print(f"❌ Error processing query: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing medical query: {str(e)}"
        )

@query_path_app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Medical Query API"
    }

if __name__ == "__main__":
    import uvicorn
    print("🏥 Starting Medical Query API Server...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔍 Example query: http://localhost:8000/search?q=Fetch cases of males over 50 diagnosed with prostate adenocarcinoma last year")
    uvicorn.run(query_path_app, host="0.0.0.0", port=8000)
