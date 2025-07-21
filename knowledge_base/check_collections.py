#!/usr/bin/env python3
"""
Quick script to check what collections exist in ChromaDB
"""
import chromadb
import os

# Disable ChromaDB telemetry
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY"] = "False"

def check_collections():
    """Check what collections exist in ChromaDB"""
    try:
        # Connect to ChromaDB
        client = chromadb.PersistentClient(path="./chroma_db")
        
        # List all collections
        collections = client.list_collections()
        
        print(f"Found {len(collections)} collections:")
        for collection in collections:
            print(f"  - Name: {collection.name}")
            print(f"    Count: {collection.count()}")
            print(f"    Metadata: {collection.metadata}")
            print()
        
        if len(collections) == 0:
            print("No collections found in the database.")
            print("You may need to run create_embeddings.py to create the collection.")
        
    except Exception as e:
        print(f"Error checking collections: {e}")

if __name__ == "__main__":
    check_collections()
