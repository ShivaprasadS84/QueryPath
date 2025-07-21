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
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib3

# Disable ChromaDB telemetry and SSL warnings
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY"] = "False"
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BatchEmbeddingProcessor:
    """Optimized batch processing for large oncology datasets"""
    
    def __init__(self, base_url: str = "http://localhost:8081/v1", batch_size: int = 32, max_workers: int = 2):
        self.base_url = base_url
        self.batch_size = batch_size
        self.max_workers = max_workers
        
        logger.info(f"Initializing batch processor with batch_size={batch_size}, max_workers={max_workers}")
        
        # Initialize nomic-embed client
        self.client = OpenAI(
            base_url=base_url,
            api_key="not-needed"
        )
        
        # Test connection and get embedding dimension
        try:
            test_embedding = self.client.embeddings.create(
                input="test",
                model="nomic-embed-text-v1.5"
            )
            self.embedding_dim = len(test_embedding.data[0].embedding)
            logger.info(f"nomic-embed model connected successfully. Embedding dimension: {self.embedding_dim}")
        except Exception as e:
            logger.error(f"Failed to connect to nomic-embed model: {e}")
            raise
    
    def process_large_dataset(self, data_path: str, collection_name: str = "oncology_snomed_large"):
        """Process large oncology dataset with optimized batching"""
        
        # Load data
        logger.info(f"Loading data from: {data_path}")
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        total_concepts = len(data)
        logger.info(f"Processing {total_concepts} concept entries")
        
        # Initialize ChromaDB
        client = chromadb.PersistentClient(path="./chroma_db")
        
        # Delete existing collection
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
                "hnsw:construction_ef": 200,
                "description": f"Large oncology SNOMED CT dataset with {total_concepts} concepts"
            }
        )
        
        # Prepare all documents
        all_documents = []
        all_texts = []
        all_ids = []
        all_metadatas = []
        
        doc_counter = 0
        
        for concept_id, aliases in tqdm(data.items(), desc="Preparing documents"):
            primary_term = aliases[0] if aliases else ""
            
            # Add primary term
            doc_id = f"{concept_id}_{doc_counter}"
            all_ids.append(doc_id)
            all_texts.append(primary_term)
            all_metadatas.append({
                "concept_id": concept_id,
                "primary_term": primary_term,
                "alias_count": len(aliases),
                "is_alias": False,
                "aliases": json.dumps(aliases)
            })
            doc_counter += 1
            
            # Add aliases
            for i, alias in enumerate(aliases[1:], 1):
                doc_id = f"{concept_id}_{doc_counter}"
                all_ids.append(doc_id)
                all_texts.append(alias)
                all_metadatas.append({
                    "concept_id": concept_id,
                    "primary_term": primary_term,
                    "alias_count": len(aliases),
                    "is_alias": True,
                    "alias_index": i,
                    "aliases": json.dumps(aliases)
                })
                doc_counter += 1
        
        total_documents = len(all_texts)
        logger.info(f"Prepared {total_documents} documents for embedding")
        
        # Generate embeddings in batches
        logger.info("Generating embeddings...")
        all_embeddings = []
        
        start_time = time.time()
        
        for i in tqdm(range(0, total_documents, self.batch_size), desc="Generating embeddings"):
            batch_texts = all_texts[i:i + self.batch_size]
            
            try:
                # Generate embeddings for batch using OpenAI API
                response = self.client.embeddings.create(
                    input=batch_texts,
                    model="nomic-embed-text-v1.5"
                )
                
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)
                
                # Small delay to avoid overwhelming the API
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error generating embeddings for batch {i}: {e}")
                # Generate fallback embeddings one by one
                batch_embeddings = []
                for text in batch_texts:
                    try:
                        response = self.client.embeddings.create(
                            input=[text],
                            model="nomic-embed-text-v1.5"
                        )
                        batch_embeddings.append(response.data[0].embedding)
                        time.sleep(0.05)
                    except Exception as e2:
                        logger.error(f"Error with text: {text[:50]}... Error: {e2}")
                        batch_embeddings.append([0.0] * self.embedding_dim)  # Fallback
                
                all_embeddings.extend(batch_embeddings)
            
            # Progress update
            if (i // self.batch_size + 1) % 10 == 0:
                elapsed = time.time() - start_time
                rate = (i + self.batch_size) / elapsed
                eta = (total_documents - i - self.batch_size) / rate if rate > 0 else 0
                logger.info(f"Processed {i + self.batch_size}/{total_documents} documents. Rate: {rate:.1f} docs/sec, ETA: {eta:.1f}s")
        
        # Add to ChromaDB in large batches
        logger.info("Adding documents to ChromaDB...")
        chromadb_batch_size = 1000
        
        for i in tqdm(range(0, total_documents, chromadb_batch_size), desc="Adding to ChromaDB"):
            batch_end = min(i + chromadb_batch_size, total_documents)
            
            try:
                collection.add(
                    ids=all_ids[i:batch_end],
                    embeddings=all_embeddings[i:batch_end],
                    documents=all_texts[i:batch_end],
                    metadatas=all_metadatas[i:batch_end]
                )
            except Exception as e:
                logger.error(f"Error adding batch {i}-{batch_end}: {e}")
                # Try smaller batches
                smaller_batch_size = 100
                for j in range(i, batch_end, smaller_batch_size):
                    small_batch_end = min(j + smaller_batch_size, batch_end)
                    try:
                        collection.add(
                            ids=all_ids[j:small_batch_end],
                            embeddings=all_embeddings[j:small_batch_end],
                            documents=all_texts[j:small_batch_end],
                            metadatas=all_metadatas[j:small_batch_end]
                        )
                    except Exception as e2:
                        logger.error(f"Error adding small batch {j}-{small_batch_end}: {e2}")
        
        final_count = collection.count()
        total_time = time.time() - start_time
        
        logger.info(f"✅ Successfully processed {total_concepts} concepts into {final_count} documents")
        logger.info(f"⏱️  Total processing time: {total_time:.2f} seconds")
        logger.info(f"📊 Average rate: {final_count / total_time:.2f} documents/second")
        
        return collection

def main():
    """Main function for batch processing"""
    
    # Configuration
    BASE_URL = "http://localhost:8081/v1"  # nomic-embed API endpoint
    
    # Choose dataset
    datasets = {
        "small": r"c:\Users\320087881\Personal\QueryPath\knowledge_base\oncology_snomed_first10.json",
        "large": r"c:\Users\320087881\Personal\QueryPath\knowledge_base\oncology_snomed_first3000.json"
    }
    
    print("📊 Available datasets:")
    for name, path in datasets.items():
        if os.path.exists(path):
            with open(path, 'r') as f:
                data = json.load(f)
            print(f"  {name}: {path} ({len(data)} concepts)")
        else:
            print(f"  {name}: {path} (NOT FOUND)")
    
    dataset_choice = input("\nChoose dataset (small/large): ").strip().lower()
    
    if dataset_choice not in datasets:
        print("❌ Invalid choice")
        return
    
    data_path = datasets[dataset_choice]
    
    if not os.path.exists(data_path):
        print(f"❌ Dataset file not found: {data_path}")
        return
    
    collection_name = f"oncology_snomed_{dataset_choice}"
    
    try:
        # Initialize processor
        processor = BatchEmbeddingProcessor(
            base_url=BASE_URL,
            batch_size=16,  # Smaller batch for stability
            max_workers=1   # Single worker for now
        )
        
        # Process dataset
        collection = processor.process_large_dataset(data_path, collection_name)
        
        print(f"\n✅ Batch processing completed!")
        print(f"📊 Collection: {collection_name}")
        print(f"📄 Documents: {collection.count()}")
        print(f"🔍 Ready for similarity search!")
        
    except Exception as e:
        logger.error(f"Batch processing failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
