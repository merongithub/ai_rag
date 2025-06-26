# ingestion.py
## This script is used to ingest data into ChromaDB from the film table in the dvdrental database.
## It uses the OpenAI API to embed the data and then stores it in ChromaDB.
## It is used to create the initial collection of films for the application.
## It only runs once to create the initial collection.

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from openai import OpenAI
import chromadb

# 1. Load environment variables
load_dotenv('config.env')

# 2. Setup configs from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME")
OPENAI_EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL")

print(f"🔧 Configuration:")
print(f"   Database URL: {DATABASE_URL}")
print(f"   Collection Name: {CHROMA_COLLECTION_NAME}")
print(f"   Embed Model: {OPENAI_EMBED_MODEL}")

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 3. Connect to database
print("🔌 Connecting to database...")
engine = create_engine(DATABASE_URL)
conn = engine.connect()

# 4. Fetch data from the film table (limited to first 100 films)
print("📊 Fetching film data...")
result = conn.execute(text("SELECT film_id, title, description FROM film WHERE film_id <= 100 ORDER BY film_id")).fetchall()
print(f"✅ Fetched {len(result)} films from database")

# 5. Connect to ChromaDB with persistent storage
print("🔗 Connecting to ChromaDB...")
chroma_client = chromadb.PersistentClient(path="./chroma_db")
print(f"✅ ChromaDB client initialized with persistent storage")

# Check existing collections
existing_collections = chroma_client.list_collections()
print(f"📋 Existing collections: {[col.name for col in existing_collections]}")

# Get or create collection
collection = chroma_client.get_or_create_collection(CHROMA_COLLECTION_NAME)
print(f"✅ Collection '{CHROMA_COLLECTION_NAME}' ready")

# Check if collection already has data
existing_count = collection.count()
print(f"📊 Collection currently contains {existing_count} documents")

if existing_count > 0:
    print("⚠️  Collection already has data. Skipping ingestion.")
else:
    print("🔄 Starting data ingestion...")
    
    # 6. Process and insert into Chroma
    for i, row in enumerate(result):
        film_id = str(row.film_id)
        text_to_embed = f"{row.title}: {row.description or ''}"
        
        print(f"📝 Processing film {i+1}/{len(result)}: {row.title}")

        # Get embedding from OpenAI using current API
        response = client.embeddings.create(
            input=text_to_embed,
            model=OPENAI_EMBED_MODEL
        )
        embedding = response.data[0].embedding

        # Store in Chroma
        collection.add(
            documents=[text_to_embed],
            embeddings=[embedding],
            ids=[film_id]
        )
        
        if (i + 1) % 10 == 0:
            print(f"✅ Processed {i+1} films...")

    print(f"✅ Data ingestion complete. Added {len(result)} films to collection.")

# Final verification
final_count = collection.count()
print(f"📊 Final collection count: {final_count} documents")

conn.close()
print("🔌 Database connection closed")
