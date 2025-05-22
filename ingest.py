import os
from dotenv import load_dotenv
import chromadb
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize ChromaDB client with the updated configuration
chroma_client = chromadb.PersistentClient(path="./chroma_store")
collection = chroma_client.get_or_create_collection("knowledge_base")

def embed(texts):
    """Generate embeddings for a list of texts using OpenAI API"""
    res = client.embeddings.create(input=texts, model="text-embedding-ada-002")
    return [d.embedding for d in res.data]

# Process each file in the data directory
for file in os.listdir("data"):
    print(f"Processing {file}...")
    with open(f"data/{file}", "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
        chunks = [chunk.strip() for chunk in content.split("\n\n") if chunk.strip()]

        # Generate embeddings for chunks
        embeddings = embed(chunks)

        # Create unique IDs for each chunk
        ids = [f"{file}-{i}" for i in range(len(chunks))]

        # Add chunks to the collection
        collection.add(
            documents=chunks,
            embeddings=embeddings,
            ids=ids,
            metadatas=[{"source": file} for _ in range(len(chunks))]  # Adding source metadata
        )

# No need to call persist() with PersistentClient as it auto-persists
print(f"✅ Data embedded and stored. Documents in collection: {collection.count()}")