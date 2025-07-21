import json
import os
import chromadb
from langchain_text_splitters.json import RecursiveJsonSplitter
from openai import OpenAI
import numpy as np
from typing import List, Dict, Any
import logging
from tqdm import tqdm
import time
import urllib3

# Disable ChromaDB telemetry and SSL warnings
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY"] = "False"
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NomicEmbeddingGenerator:
    """Embedding generator using nomic-embed model via OpenAI API"""
    
    def __init__(self, base_url: str = "http://localhost:8081/v1"):
        self.base_url = base_url
        
        logger.info(f"Initializing nomic-embed client with base_url: {base_url}")
        self.client = OpenAI(
            base_url=base_url,
            api_key="not-needed",
            timeout=30.0
        )
        
        # Test connection
        try:
            logger.info("Testing connection to nomic-embed API...")
            test_embedding = self.client.embeddings.create(
                input="test",
                model="nomic-embed-text-v1.5"
            )
            self.embedding_dim = len(test_embedding.data[0].embedding)
            logger.info(f"✅ nomic-embed model connected successfully. Embedding dimension: {self.embedding_dim}")
        except Exception as e:
            error_msg = str(e)
            if "501" in error_msg and "embeddings" in error_msg:
                logger.error("❌ Server does not support embeddings. Please start your server with the --embeddings flag")
                logger.error("💡 Example: python -m llama_cpp.server --model your_model.gguf --embeddings --port 8081")
            elif "Connection" in error_msg or "timeout" in error_msg.lower():
                logger.error(f"❌ Cannot connect to server at {base_url}. Please ensure the server is running.")
            else:
                logger.error(f"❌ Failed to connect to nomic-embed model: {e}")
            
            logger.error("🔧 Troubleshooting steps:")
            logger.error("   1. Ensure your embedding server is running on port 8081")
            logger.error("   2. Start the server with --embeddings flag")
            logger.error("   3. Check if the endpoint is accessible: curl http://localhost:8081/v1/models")
            raise
    
    def encode(self, texts: List[str], batch_size: int = 32, show_progress_bar: bool = True) -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        embeddings = []
        
        iterator = tqdm(range(0, len(texts), batch_size), desc="Generating embeddings") if show_progress_bar else range(0, len(texts), batch_size)
        
        for i in iterator:
            batch = texts[i:i + batch_size]
            
            try:
                # Generate embeddings for batch using OpenAI API
                response = self.client.embeddings.create(
                    input=batch,
                    model="nomic-embed-text-v1.5"
                )
                
                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)
                
                # Small delay to avoid overwhelming the API
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error generating embeddings for batch {i}: {e}")
                # Generate fallback embeddings one by one
                batch_embeddings = []
                for text in batch:
                    try:
                        response = self.client.embeddings.create(
                            input=[text],
                            model="nomic-embed-text-v1.5"
                        )
                        batch_embeddings.append(response.data[0].embedding)
                        time.sleep(0.05)
                    except Exception as e2:
                        logger.error(f"Error generating embedding for text: {text[:50]}... Error: {e2}")
                        # Use zero embedding as fallback
                        batch_embeddings.append([0.0] * self.embedding_dim)
                
                embeddings.extend(batch_embeddings)
        
        return embeddings

class JSONDocumentSplitter:
    """Custom JSON document splitter using RecursiveJsonSplitter"""
    
    def __init__(self, max_chunk_size: int = 1000, min_chunk_size: int = 100):
        self.splitter = RecursiveJsonSplitter(
            max_chunk_size=max_chunk_size,
            min_chunk_size=min_chunk_size
        )
    
    def split_json_data(self, json_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Split JSON data into chunks while preserving structure"""
        try:
            # Split the JSON data
            chunks = self.splitter.split_json(json_data, convert_lists=False)
            return chunks
        except Exception as e:
            logger.error(f"Error splitting JSON data: {e}")
            return [json_data]  # Return original data as fallback

def load_oncology_data(file_path: str) -> Dict[str, List[str]]:
    """Load oncology SNOMED data from JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def prepare_documents_for_embedding(data: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    """Prepare documents for embedding with proper metadata"""
    documents = []
    
    for concept_id, aliases in data.items():
        # Primary term (first alias)
        primary_term = aliases[0] if aliases else ""
        
        # Create document for primary term
        doc = {
            "concept_id": concept_id,
            "primary_term": primary_term,
            "aliases": aliases,
            "text": primary_term,
            "alias_count": len(aliases)
        }
        documents.append(doc)
        
        # Create separate documents for each alias
        for i, alias in enumerate(aliases):
            if i > 0:  # Skip primary term as it's already added
                alias_doc = {
                    "concept_id": concept_id,
                    "primary_term": primary_term,
                    "aliases": aliases,
                    "text": alias,
                    "alias_count": len(aliases),
                    "is_alias": True,
                    "alias_index": i
                }
                documents.append(alias_doc)
    
    return documents

def create_chromadb_collection(data_path: str, base_url: str = "http://localhost:8081/v1", collection_name: str = "oncology_snomed"):
    """Create ChromaDB collection with embeddings"""
    
    # Initialize ChromaDB client
    client = chromadb.PersistentClient(path="./chroma_db")
    
    # Delete existing collection if it exists
    try:
        client.delete_collection(name=collection_name)
        logger.info(f"Deleted existing collection: {collection_name}")
    except:
        pass
    
    # Create new collection
    collection = client.create_collection(
        name=collection_name,
        metadata={
            "hnsw:space": "cosine",
            "hnsw:search_ef": 500,
            "description": "Oncology SNOMED CT terms with aliases using nomic-embed"
        }
    )
    
    # Load data
    logger.info(f"Loading data from: {data_path}")
    oncology_data = load_oncology_data(data_path)
    logger.info(f"Loaded {len(oncology_data)} concept entries")
    
    # Prepare documents
    documents = prepare_documents_for_embedding(oncology_data)
    logger.info(f"Prepared {len(documents)} documents for embedding")
    
    # Initialize embedding generator
    embedding_generator = NomicEmbeddingGenerator(base_url)
    
    # Extract texts for embedding
    texts = [doc["text"] for doc in documents]
    
    # Generate embeddings
    logger.info("Generating embeddings...")
    embeddings = embedding_generator.encode(texts, batch_size=16, show_progress_bar=True)
    
    # Prepare data for ChromaDB
    ids = [f"{doc['concept_id']}_{i}" for i, doc in enumerate(documents)]
    metadatas = []
    
    for doc in documents:
        metadata = {
            "concept_id": doc["concept_id"],
            "primary_term": doc["primary_term"],
            "alias_count": doc["alias_count"],
            "is_alias": doc.get("is_alias", False),
            "aliases": json.dumps(doc["aliases"])  # Store as JSON string
        }
        if doc.get("alias_index"):
            metadata["alias_index"] = doc["alias_index"]
        metadatas.append(metadata)
    
    # Add to collection in batches
    batch_size = 500
    logger.info(f"Adding {len(documents)} documents to ChromaDB...")
    
    for i in tqdm(range(0, len(documents), batch_size), desc="Adding to ChromaDB"):
        batch_end = min(i + batch_size, len(documents))
        
        collection.add(
            ids=ids[i:batch_end],
            embeddings=embeddings[i:batch_end],
            documents=texts[i:batch_end],
            metadatas=metadatas[i:batch_end]
        )
    
    logger.info(f"Successfully created collection '{collection_name}' with {collection.count()} documents")
    return collection

if __name__ == "__main__":
    # Configuration
    DATA_PATH = os.path.join(os.path.dirname(__file__), "oncology_snomed_first3000.json")
    BASE_URL = "http://localhost:8081/v1"  # nomic-embed API endpoint
    COLLECTION_NAME = "oncology_snomed_test"
    
    try:
        # Create the collection
        collection = create_chromadb_collection(DATA_PATH, BASE_URL, COLLECTION_NAME)
        print(f"\n✅ Successfully created ChromaDB collection with {collection.count()} documents")
        print(f"📊 Collection name: {COLLECTION_NAME}")
        print(f"🔍 Ready for similarity search!")
        print(f"🌐 Using nomic-embed model at: {BASE_URL}")
        
    except Exception as e:
        logger.error(f"Error creating collection: {e}")
        raise
