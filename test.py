import chromadb

# New way to create a client
client = chromadb.PersistentClient(path="./chroma_store")

# Then create or get your collection
collection = client.get_or_create_collection("test_collection")

print(f"Document count: {collection.count()}")