import chromadb

from embedding_demo import get_embedding

VECTOR_STORE_PATH = "vector_store"
COLLECTION_NAME = "devops_docs_600"

def main() -> None:
    # Create Chroma persistent client to save data to disk
    client = chromadb.PersistentClient(
        path=VECTOR_STORE_PATH
    )

    # Get an already existing collection
    # TODO: check what if we need a new collection
    collection = client.get_collection(
        name=COLLECTION_NAME
    )

    question = "What is a ConfigMap used for?"
    # Embed the question
    query_embedding = get_embedding(question)

    # Search collection for similar embeddings
    # We can send multiple queries but send only one here in a list
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=5,
        include=[
            "documents",
            "metadatas",
            "distances",
        ],
    )

    # We need to extract the reply for index 0
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for index, (document, metadata,distance) in enumerate(
        zip(documents, metadatas, distances),
        start=1,
    ):
        print(f"Result {index}")
        print(f"Distance: {distance}")
        print(f"Source: {metadata['source']}")
        print(f"Section: {metadata['section']}")
        print(document)
        print("-" * 60)

if __name__ == "__main__":
    main()
