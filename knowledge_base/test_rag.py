import json
import os
from create_embeddings import create_chromadb_collection, load_oncology_data
from rag_query import SnomedRAGSystem
import urllib3

# Disable ChromaDB telemetry and SSL warnings
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY"] = "False"
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_system():
    """Test the RAG system with sample queries"""
    
    # Configuration - using relative paths
    DATA_PATH = os.path.join(os.path.dirname(__file__), "snomed_new.json")
    BASE_URL = "http://localhost:8081/v1"  # nomic-embed API endpoint
    COLLECTION_NAME = "snomed_new_test"
    
    print("🧪 Testing SNOMED CT RAG System")
    print("=" * 50)
    
    # Check if files exist
    if not os.path.exists(DATA_PATH):
        print(f"❌ Data file not found: {DATA_PATH}")
        return
    
    # Load and display data info
    data = load_oncology_data(DATA_PATH)
    print(f"📊 Loaded {len(data)} concept entries")
    
    # Sample some entries
    print("\n📋 Sample entries:")
    for i, (concept_id, aliases) in enumerate(list(data.items())[:3]):
        print(f"  {i+1}. {concept_id}: {aliases[0]} ({len(aliases)} aliases)")
    
    try:
        # Create embeddings
        print(f"\n🔄 Creating embeddings collection...")
        collection = create_chromadb_collection(DATA_PATH, BASE_URL, COLLECTION_NAME)
        print(f"✅ Collection created with {collection.count()} documents")
        
        # Initialize RAG system
        print(f"\n🔄 Initializing RAG system...")
        rag_system = SnomedRAGSystem(BASE_URL, COLLECTION_NAME)
        
        # Test queries
        test_queries = [
            "lung cancer",
            "leukemia",
            "lymphoma",
            "carcinoma",
            "tumor"
        ]
        
        print(f"\n🔍 Testing with sample queries:")
        for query in test_queries:
            print(f"\n--- Query: '{query}' ---")
            results = rag_system.search_similar_terms(query, top_k=3)
            
            if results:
                for i, result in enumerate(results, 1):
                    print(f"  {i}. {result.primary_term} (ID: {result.concept_id})")
                    print(f"     Similarity: {result.similarity_score:.3f}")
                    print(f"     Aliases: {len(result.aliases)}")
            else:
                print("  No results found")
        
        print(f"\n✅ Test completed successfully!")
        print(f"💡 Run 'python rag_query.py' for interactive search")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_system()
