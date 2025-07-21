# Oncology SNOMED CT RAG System

A comprehensive Retrieval-Augmented Generation (RAG) system for oncology SNOMED CT terms using RecursiveJsonSplitter, nomic-embed embeddings, and ChromaDB.

## 🏗️ Architecture

```
Query → nomic-embed API → ChromaDB Vector Search → Ranked Results
                                      ↑
JSON Data → RecursiveJsonSplitter → Document Chunks → Embeddings
```

## 📁 Files Overview

- **`create_embeddings.py`** - Main embedding creation script
- **`rag_query.py`** - Interactive RAG query system
- **`batch_embeddings.py`** - Optimized batch processing for large datasets
- **`test_rag.py`** - System testing and verification
- **`requirements.txt`** - Python dependencies

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Create Embeddings Database

```bash
python create_embeddings.py
```

This will:
- Load oncology SNOMED data from `oncology_snomed_first10.json`
- Split JSON data using RecursiveJsonSplitter
- Generate embeddings using GIST-Large model
- Store in ChromaDB with metadata preservation

### 3. Run Interactive Search

```bash
python rag_query.py
```

## 🔧 Configuration

### API Endpoint
```python
BASE_URL = "http://localhost:8081/v1"  # nomic-embed API endpoint
```

### Data Path
```python
DATA_PATH = r"c:\Users\320087881\Personal\QueryPath\knowledge_base\oncology_snomed_first10.json"
```

## 📊 Features

### 🎯 Smart JSON Splitting
- Uses `RecursiveJsonSplitter` from LangChain
- Preserves JSON hierarchy and structure
- Configurable chunk sizes (default: 1000 max, 100 min)
- Handles nested structures and lists

### 🧠 nomic-embed Embeddings
- High-quality embeddings via OpenAI-compatible API
- 768-dimensional vectors (nomic-embed-text-v1.5)
- Optimized for semantic similarity
- Batch processing support

### 🗄️ ChromaDB Vector Database
- Persistent storage with cosine similarity
- Metadata preservation for concept IDs and aliases
- Efficient similarity search with HNSW indexing
- Batch insertion for large datasets

### 🔍 Advanced Search Features
- **Semantic Search**: Natural language queries
- **Concept ID Search**: Direct lookup by SNOMED ID
- **Alias Matching**: Searches across all term variations
- **Similarity Scoring**: Ranked results with confidence scores

## 📋 Data Structure

### Input JSON Format
```json
{
    "concept_id": [
        "Primary Term",
        "Alias 1",
        "Alias 2",
        "..."
    ]
}
```

### Stored Metadata
```json
{
    "concept_id": "10069009",
    "primary_term": "Giant cell tumor of bone, malignant",
    "alias_count": 4,
    "is_alias": false,
    "aliases": "[\"Giant cell tumor of bone, malignant\", \"Malignant giant cell tumor of bone\", ...]"
}
```

## 🎮 Usage Examples

### Interactive Search
```
🔍 Enter your query: lung cancer
```

### Concept ID Search
```
🔍 Enter your query: ID:10069009
```

### Programmatic Usage
```python
from rag_query import OncologyRAGSystem

# Initialize system
rag = OncologyRAGSystem(base_url="http://localhost:8081/v1", collection_name="oncology_snomed")

# Search for similar terms
results = rag.search_similar_terms("lung cancer", top_k=5)

# Search by concept ID
results = rag.search_by_concept_id("10069009")
```

## 🔄 Batch Processing

For large datasets (3000+ concepts), use the optimized batch processor:

```bash
python batch_embeddings.py
```

Features:
- Memory-efficient processing
- Progress tracking with ETA
- Error handling and recovery
- Configurable batch sizes

## 🧪 Testing

Run the test suite to verify system functionality:

```bash
python test_rag.py
```

This will:
- Create a test collection
- Run sample queries
- Verify embedding generation
- Test similarity search

## 📈 Performance

### Embedding Generation
- **Small dataset (10 concepts)**: ~30 seconds
- **Large dataset (3000 concepts)**: ~45 minutes
- **Rate**: ~2-3 documents/second (includes aliases)

### Search Performance
- **Query embedding**: ~0.5 seconds
- **Vector search**: ~0.1 seconds
- **Total response time**: ~0.6 seconds

## 🛠️ Customization

### Adjust Chunk Sizes
```python
splitter = RecursiveJsonSplitter(
    max_chunk_size=2000,  # Increase for larger chunks
    min_chunk_size=200    # Adjust minimum size
)
```

### Modify Search Parameters
```python
results = collection.query(
    query_embeddings=[embedding],
    n_results=10,         # Number of results
    include=['documents', 'metadatas', 'distances']
)
```

### Configure ChromaDB
```python
collection = client.create_collection(
    name="custom_collection",
    metadata={
        "hnsw:space": "cosine",      # Distance metric
        "hnsw:search_ef": 500,       # Search quality
        "hnsw:construction_ef": 200  # Index construction
    }
)
```

## 🔍 Search Strategies

### 1. Semantic Similarity
Best for: Natural language queries, symptom descriptions
```
"lung tumor" → "Malignant neoplasm of lung"
```

### 2. Exact Term Matching
Best for: Known medical terms, abbreviations
```
"AML" → "Acute myeloid leukemia"
```

### 3. Concept ID Lookup
Best for: Specific SNOMED CT code retrieval
```
"ID:103688009" → All aliases for that concept
```

## 🚨 Troubleshooting

### API Connection Issues
- Ensure nomic-embed server is running on port 8081
- Check API endpoint accessibility: `http://localhost:8081/v1`
- Verify OpenAI client installation

### ChromaDB Errors
- Delete existing collection if schema changes
- Check disk space for database storage
- Verify write permissions in database directory

### Embedding Generation Failures
- Reduce batch size for memory constraints
- Check text encoding (UTF-8 required)
- Monitor system resources during processing

## 📚 Dependencies

- **chromadb**: Vector database
- **langchain-text-splitters**: JSON document splitting
- **openai**: API client for nomic-embed
- **numpy**: Numerical operations
- **tqdm**: Progress bars

## 🎯 Use Cases

1. **Medical Term Standardization**: Map clinical notes to SNOMED CT codes
2. **Symptom-to-Diagnosis Mapping**: Find relevant oncology terms from descriptions
3. **Medical Coding Assistance**: Help coders find appropriate SNOMED CT terms
4. **Research Query Expansion**: Expand search terms with related concepts
5. **Clinical Decision Support**: Retrieve relevant oncology information

## 🔮 Future Enhancements

- [ ] Multi-language support
- [ ] Hierarchical SNOMED CT relationships
- [ ] Real-time embedding updates
- [ ] API endpoint for web integration
- [ ] Advanced filtering by medical categories
- [ ] Fuzzy matching for misspelled terms

## 📄 License

This project is part of the QueryPath medical information system.
