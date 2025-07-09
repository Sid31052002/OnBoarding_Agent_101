import chromadb

client = chromadb.PersistentClient(path="backend/vector_store/db")

print("Collections:", client.list_collections())

try:
    collection = client.get_collection("faq")
except Exception as e:
    print("Collection 'faq' not found:", e)
    exit()

results = collection.get(include=["documents", "metadatas"])

if not results["documents"]:
    print("No documents found in 'faq' collection.")
else:
    for i, doc in enumerate(results["documents"]):
        print(f"--- Chunk {i+1} ---")
        print(doc)
        print(f"Metadata: {results['metadatas'][i]}")
        print()
