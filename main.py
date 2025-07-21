from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from models import SearchResponse
from agent import UnifiedMedicalQueryClient

query_path_app = FastAPI(title="Medical Query API", description="Unified medical query processing API")

# Initialize the medical query client
medical_client = UnifiedMedicalQueryClient()

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
        # Process the medical query using the unified agent
        result = await medical_client.process_medical_query(q)
        
        # Debug: Print the raw result
        print(f"🔍 Raw agent result: {result}")
        
        # Convert the result to match the SearchResponse model
        response_data = {
            "patient_info": result.get("patient_info", {}),
        }
        
        # Handle temporal_info if it exists
        if result.get("temporal_info"):
            response_data["temporal_info"] = result["temporal_info"]
        
        # Add errors if they exist
        if result.get("errors"):
            response_data["errors"] = result["errors"]
        
        print(f"🔍 Response data before validation: {response_data}")
            
        return SearchResponse(**response_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

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
