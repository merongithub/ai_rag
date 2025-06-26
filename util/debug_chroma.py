#!/usr/bin/env python3
"""
Debug script to check ChromaDB collection status
"""

import os
from dotenv import load_dotenv
import chromadb
from sqlalchemy import create_engine, text
from openai import OpenAI

# Load environment variables
load_dotenv('config.env')

print("🔍 Debugging ChromaDB Collection")
print("=" * 50)

# Initialize ChromaDB
chroma_client = chromadb.Client()
print(f"✅ ChromaDB client initialized")

# Check all collections
collections = chroma_client.list_collections()
print(f"📋 Available collections: {[col.name for col in collections]}")

# Get the films collection
collection_name = os.getenv("CHROMA_COLLECTION_NAME", "films")
print(f"🎯 Target collection name: {collection_name}")

try:
    collection = chroma_client.get_collection(name=collection_name)
    print(f"✅ Collection '{collection_name}' found")
    
    # Check collection count
    count = collection.count()
    print(f"📊 Collection contains {count} documents")
    
    if count > 0:
        # Get a sample document
        sample = collection.get(limit=1)
        print(f"📄 Sample document ID: {sample['ids'][0]}")
        print(f"📄 Sample document content: {sample['documents'][0][:100]}...")
    else:
        print("❌ Collection is empty!")
        
except Exception as e:
    print(f"❌ Error accessing collection: {e}")

print("\n🔍 Checking database connection...")
try:
    engine = create_engine(os.getenv("DATABASE_URL"))
    conn = engine.connect()
    
    # Check if we can get film data
    result = conn.execute(text("SELECT COUNT(*) FROM film")).fetchone()
    print(f"📊 Database contains {result[0]} films")
    
    # Get a sample film
    sample_film = conn.execute(text("SELECT film_id, title, description FROM film LIMIT 1")).fetchone()
    print(f"📄 Sample film: ID={sample_film.film_id}, Title='{sample_film.title}'")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Database error: {e}")

print("\n🔍 Manual data ingestion test...")
try:
    # Initialize OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Get a sample film for testing
    engine = create_engine(os.getenv("DATABASE_URL"))
    conn = engine.connect()
    sample_film = conn.execute(text("SELECT film_id, title, description FROM film LIMIT 1")).fetchone()
    conn.close()
    
    if sample_film:
        text_to_embed = f"{sample_film.title}: {sample_film.description or ''}"
        print(f"📝 Testing with: {text_to_embed[:100]}...")
        
        # Get embedding
        response = client.embeddings.create(
            input=text_to_embed,
            model=os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
        )
        embedding = response.data[0].embedding
        print(f"✅ Embedding created (length: {len(embedding)})")
        
        # Add to collection
        collection = chroma_client.get_or_create_collection(collection_name)
        collection.add(
            documents=[text_to_embed],
            embeddings=[embedding],
            ids=[f"test_{sample_film.film_id}"]
        )
        print(f"✅ Test document added to collection")
        
        # Check count again
        new_count = collection.count()
        print(f"📊 Collection now contains {new_count} documents")
        
except Exception as e:
    print(f"❌ Manual ingestion error: {e}")

print("\n✅ Debug complete!") 