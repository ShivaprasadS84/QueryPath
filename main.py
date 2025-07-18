from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from models import SearchResponse
from parsers.age_parser import parse_age
from parsers.gender_parser import parse_gender
from parsers.time_parser import parse_time

query_path_app = FastAPI()

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
def search(search_query_string: str = Query(..., alias="q")):
    normalized_query = search_query_string.lower()

    search_result = {
        # TODO: Implement value extraction of diagnosis field
        "diagnosis": None,
    }

    age_details = parse_age(normalized_query)
    gender = parse_gender(normalized_query)
    time_details = parse_time(normalized_query)
    search_result.update(age_details)
    search_result["gender"] = gender
    search_result.update(time_details)

    return search_result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(query_path_app, host="0.0.0.0", port=8000)
