#!/usr/bin/env python3
"""
Server Check Script
Diagnoses issues with the nomic-embed server
"""

import os
import requests
import json
from openai import OpenAI
import urllib3

# Disable SSL warnings and telemetry
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY"] = "False"
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def check_server_status(base_url: str = "http://localhost:8081"):
    """Check if the server is running and what endpoints are available"""
    
    print("🔍 Checking nomic-embed server status...")
    print(f"📍 Base URL: {base_url}")
    print("-" * 50)
    
    # Test basic connectivity
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"✅ Server is running (Status: {response.status_code})")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is it running?")
        print("💡 Start your server with: python -m llama_cpp.server --model your_model.gguf --embeddings --port 8081")
        return False
    except Exception as e:
        print(f"⚠️  Health check failed: {e}")
    
    # Check available models
    try:
        response = requests.get(f"{base_url}/v1/models", timeout=5)
        if response.status_code == 200:
            models = response.json()
            print(f"📋 Available models: {json.dumps(models, indent=2)}")
        else:
            print(f"⚠️  Models endpoint returned: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Cannot check models: {e}")
    
    # Test embeddings endpoint
    print("\n🧪 Testing embeddings endpoint...")
    try:
        client = OpenAI(
            base_url=f"{base_url}/v1",
            api_key="not-needed",
            timeout=10.0
        )
        
        response = client.embeddings.create(
            input="test",
            model="nomic-embed-text-v1.5"
        )
        
        embedding_dim = len(response.data[0].embedding)
        print(f"✅ Embeddings working! Dimension: {embedding_dim}")
        print(f"📊 Sample embedding (first 5 values): {response.data[0].embedding[:5]}")
        return True
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Embeddings test failed: {e}")
        
        if "501" in error_msg:
            print("💡 Server doesn't support embeddings. Start with --embeddings flag")
            print("   Example: python -m llama_cpp.server --model your_model.gguf --embeddings --port 8081")
        elif "timeout" in error_msg.lower():
            print("💡 Server is slow to respond. Try increasing timeout or check server resources")
        elif "404" in error_msg:
            print("💡 Embeddings endpoint not found. Check if server supports OpenAI API format")
        
        return False

def test_different_models():
    """Test different model names that might work"""
    
    print("\n🔄 Testing different model names...")
    base_url = "http://localhost:8081/v1"
    
    model_names = [
        "nomic-embed-text-v1.5",
        "nomic-embed-text",
        "nomic-embed",
        "text-embedding-ada-002",  # Common fallback
        "embedding",
        "default"
    ]
    
    client = OpenAI(
        base_url=base_url,
        api_key="not-needed",
        timeout=5.0
    )
    
    for model_name in model_names:
        try:
            print(f"   Testing model: {model_name}")
            response = client.embeddings.create(
                input="test",
                model=model_name
            )
            embedding_dim = len(response.data[0].embedding)
            print(f"   ✅ {model_name} works! Dimension: {embedding_dim}")
            return model_name
        except Exception as e:
            print(f"   ❌ {model_name} failed: {str(e)[:100]}...")
    
    print("   ❌ No working model names found")
    return None

def main():
    """Main diagnostic function"""
    
    print("🏥 nomic-embed Server Diagnostic Tool")
    print("=" * 50)
    
    # Check server
    server_ok = check_server_status()
    
    if not server_ok:
        print("\n🔧 Troubleshooting Tips:")
        print("1. Make sure your embedding server is running")
        print("2. Start with --embeddings flag: --embeddings")
        print("3. Check the port: --port 8081")
        print("4. Verify the model supports embeddings")
        print("\nExample command:")
        print("python -m llama_cpp.server --model nomic-embed-text-v1.5.gguf --embeddings --port 8081")
        return
    
    # Test different models if basic test failed
    working_model = test_different_models()
    
    if working_model:
        print(f"\n✅ Success! Use model name: '{working_model}'")
        print("You can now run create_embeddings.py")
    else:
        print("\n❌ No working model configuration found")
        print("Please check your server configuration")

if __name__ == "__main__":
    main()
