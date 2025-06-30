import os
from dotenv import load_dotenv
from openai import OpenAI
import chromadb

# Load environment variables
load_dotenv('config.env')

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize ChromaDB with persistent storage
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="films")

async def ask(query: str):
    try:
        print(f"🔍 Processing query: '{query}'")
        
        # Check if collection has data
        collection_count = collection.count()
        print(f"📊 Collection contains {collection_count} documents")
        
        if collection_count == 0:
            return {
                "answer": "Error: No documents found in the collection. Please run the data ingestion script first.",
                "context": ""
            }
        
        # Get embedding for the query
        print("🤖 Getting query embedding...")
        response = client.embeddings.create(
            input=query,
            model="text-embedding-3-small"
        )
        query_embedding = response.data[0].embedding
        print(f"✅ Query embedding created (length: {len(query_embedding)})")
        
        # Query ChromaDB
        print("🔎 Querying ChromaDB...")
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=5
        )
        
        print(f"📋 ChromaDB results: {results}")
        
        # Extract documents
        documents = results["documents"][0] if results["documents"] else []
        print(f"📄 Found {len(documents)} relevant documents")
        
        if not documents:
            return {
                "answer": "I don't know the answer to that question. No relevant information found in the database.",
                "context": ""
            }
        
        context = "\n".join(documents)
        print(f"📝 Context length: {len(context)} characters")
        print(f"📝 Context preview: {context[:200]}...")
        
        # Create prompt
        prompt = f"""You are a helpful film expert. Answer the question based on the context below. 
If the question cannot be answered based on the context, say 'I don't know the answer to that question based on the available information.'

Context: {context}

Question: {query}

Answer:"""
        
        print(f"📤 Sending prompt to OpenAI (length: {len(prompt)} characters)")
        
        # Get response from OpenAI
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7  # Controls randomness (0-2, lower is more focused)
        )
        
        answer = response.choices[0].message.content
        print(f"✅ OpenAI response: {answer}")
        
        return {
            "answer": answer,
            "context": context
        }
        
    except Exception as e:
        print(f"❌ Error in ask function: {str(e)}")
        return {
            "answer": f"Error: {str(e)}",
            "context": ""
        }