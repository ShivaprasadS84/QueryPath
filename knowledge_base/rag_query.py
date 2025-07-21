import json
import os
import chromadb
from openai import OpenAI
import logging
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import re
import urllib3

# Disable ChromaDB telemetry and SSL warnings
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY"] = "False"
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Data class for search results"""
    concept_id: str
    primary_term: str
    matched_text: str
    aliases: List[str]
    similarity_score: float
    is_alias: bool = False
    alias_index: int = None

class SnomedRAGSystem:
    """RAG system for SNOMED CT queries"""
    
    def __init__(self, base_url: str = "http://localhost:8081/v1", collection_name: str = "snomed_new_batch_embeddings", db_path: str = "./chroma_db"):
        self.base_url = base_url
        self.collection_name = collection_name
        self.db_path = db_path
        
        # Initialize embedding model
        logger.info(f"Initializing nomic-embed client with base_url: {base_url}")
        self.embedding_client = OpenAI(
            base_url=base_url,
            api_key="not-needed"
        )
        
        # Test connection and get embedding dimension
        try:
            test_embedding = self.embedding_client.embeddings.create(
                input="test",
                model="nomic-embed-text-v1.5"
            )
            self.embedding_dim = len(test_embedding.data[0].embedding)
            logger.info(f"nomic-embed model connected successfully. Embedding dimension: {self.embedding_dim}")
        except Exception as e:
            logger.error(f"Failed to connect to nomic-embed model: {e}")
            raise
        
        # Initialize ChromaDB client
        self.chroma_client = chromadb.PersistentClient(path=db_path)
        
        try:
            self.collection = self.chroma_client.get_collection(name=collection_name)
            logger.info(f"Connected to collection '{collection_name}' with {self.collection.count()} documents")
        except Exception as e:
            logger.error(f"Error connecting to collection '{collection_name}': {e}")
            logger.info("Please run create_embeddings.py first to create the collection")
            raise
    
    def generate_query_embedding(self, query: str) -> List[float]:
        """Generate embedding for query text"""
        try:
            response = self.embedding_client.embeddings.create(
                input=[query],
                model="nomic-embed-text-v1.5"
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding for query: {query}. Error: {e}")
            return [0.0] * self.embedding_dim  # Fallback zero embedding
    
    def search_similar_terms(self, query: str, top_k: int = 10) -> List[SearchResult]:
        """Search for similar oncology terms"""
        
        # Generate query embedding
        query_embedding = self.generate_query_embedding(query)
        
        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=['documents', 'metadatas', 'distances']
        )
        
        # Process results
        search_results = []
        
        for i in range(len(results['ids'][0])):
            metadata = results['metadatas'][0][i]
            document = results['documents'][0][i]
            distance = results['distances'][0][i]
            
            # Convert distance to similarity score (cosine distance to similarity)
            similarity_score = 1 - distance
            
            # Parse aliases from JSON string
            aliases = json.loads(metadata['aliases'])
            
            result = SearchResult(
                concept_id=metadata['concept_id'],
                primary_term=metadata['primary_term'],
                matched_text=document,
                aliases=aliases,
                similarity_score=similarity_score,
                is_alias=metadata.get('is_alias', False),
                alias_index=metadata.get('alias_index')
            )
            
            search_results.append(result)
        
        return search_results
    
    def search_by_concept_id(self, concept_id: str) -> List[SearchResult]:
        """Search by specific concept ID"""
        
        results = self.collection.query(
            query_embeddings=None,
            where={"concept_id": concept_id},
            n_results=100,  # Get all results for this concept
            include=['documents', 'metadatas', 'distances']
        )
        
        search_results = []
        
        for i in range(len(results['ids'][0])):
            metadata = results['metadatas'][0][i]
            document = results['documents'][0][i]
            
            aliases = json.loads(metadata['aliases'])
            
            result = SearchResult(
                concept_id=metadata['concept_id'],
                primary_term=metadata['primary_term'],
                matched_text=document,
                aliases=aliases,
                similarity_score=1.0,  # Exact match
                is_alias=metadata.get('is_alias', False),
                alias_index=metadata.get('alias_index')
            )
            
            search_results.append(result)
        
        return search_results
    
    def format_results(self, results: List[SearchResult], show_aliases: bool = True) -> str:
        """Format search results for display"""
        
        if not results:
            return "No results found."
        
        formatted = []
        formatted.append(f"🔍 Found {len(results)} similar terms:\n")
        
        # Group results by concept_id to avoid duplicates
        concept_groups = {}
        for result in results:
            if result.concept_id not in concept_groups:
                concept_groups[result.concept_id] = result
            elif result.similarity_score > concept_groups[result.concept_id].similarity_score:
                concept_groups[result.concept_id] = result
        
        for i, (concept_id, result) in enumerate(concept_groups.items(), 1):
            formatted.append(f"{i}. 🏷️  **{result.primary_term}**")
            formatted.append(f"   📋 Concept ID: {result.concept_id}")
            formatted.append(f"   📊 Similarity: {result.similarity_score:.3f}")
            formatted.append(f"   🎯 Matched: \"{result.matched_text}\"")
            
            if show_aliases and len(result.aliases) > 1:
                formatted.append(f"   🔗 Aliases ({len(result.aliases)-1}):")
                for alias in result.aliases[1:]:  # Skip primary term
                    formatted.append(f"      • {alias}")
            
            formatted.append("")  # Empty line between results
        
        return "\n".join(formatted)
    
    def interactive_search(self):
        """Interactive search interface"""
        
        print("🏥 Oncology SNOMED CT RAG System")
        print("=" * 50)
        print(f"📊 Database contains {self.collection.count()} documents")
        print("💡 Enter your search query or 'quit' to exit")
        print("💡 Use 'ID:<concept_id>' to search by specific concept ID")
        print("-" * 50)
        
        while True:
            try:
                query = input("\n🔍 Enter your query: ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if not query:
                    print("❌ Please enter a valid query")
                    continue
                
                # Check if it's a concept ID search
                if query.upper().startswith('ID:'):
                    concept_id = query[3:].strip()
                    print(f"\n🔍 Searching for concept ID: {concept_id}")
                    results = self.search_by_concept_id(concept_id)
                else:
                    print(f"\n🔍 Searching for: '{query}'")
                    results = self.search_similar_terms(query, top_k=5)
                
                # Display results
                print(self.format_results(results))
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                logger.error(f"Error during search: {e}")
                print(f"❌ Error: {e}")

def main():
    """Main function"""
    
    # Configuration - using new collection name
    BASE_URL = "http://localhost:8081/v1"  # nomic-embed API endpoint
    COLLECTION_NAME = "snomed_new_batch_embeddings"
    DB_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")
    
    try:
        # Initialize RAG system
        rag_system = SnomedRAGSystem(
            base_url=BASE_URL,
            collection_name=COLLECTION_NAME,
            db_path=DB_PATH
        )
        
        # Start interactive search
        rag_system.interactive_search()
        
    except Exception as e:
        logger.error(f"Error initializing RAG system: {e}")
        print(f"❌ Error: {e}")
        print("💡 Make sure to run create_embeddings.py first to create the database")

if __name__ == "__main__":
    main()
