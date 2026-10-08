import chromadb
import requests
from embedding_demo import get_embedding

OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
CHAT_MODEL = "qwen3:8b"

VECTOR_STORE_PATH = "vector_store"
COLLECTION_NAME = "devops_docs_600"
MAX_DISTANCE = 0.7

def ask_llm(question: str, context: str) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                "Answer using only the provided context. "
                "Do not add unsupported facts. "
                "If the context is insufficient, say so. "
            ),
        },
        {
            "role": "user",
            "content": (
                f"Context:\n{context}\n\n"
                f"Question:\n{question}"
            ),
        },
    ]

    request_body = {
        "model": CHAT_MODEL,
        "messages": messages,
        "stream": False,
    }

    response = requests.post(
        OLLAMA_CHAT_URL,
        json=request_body,
        timeout=120,
    )

    # Make sure to catch error response
    response.raise_for_status()

    response_data = response.json()
    return response_data["message"]["content"]

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

    question = "How does Kubernetes expose pods?"
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

    relevant_items = []

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances,
    ):
        if distance <= MAX_DISTANCE:
            relevant_items.append({
                "document": document,
                "metadata": metadata,
                "distance": distance,
            }
        )

    if not relevant_items:
        print("No sufficiently relevant information was found.")
        return

    context_parts = []

    for item in relevant_items:
        document = item["document"]
        metadata = item["metadata"]

        context_parts.append(
            (
                f"[Source: {metadata['source']} | "
                f"Section: {metadata['section']}]\n"
                f"{document}"
            )
        )

    context = "\n\n".join(context_parts)

    answer = ask_llm(
        question=question,
        context=context,
    )

    print("Answer:")
    print(answer)

    print()
    print("Sources:")

    seen_sources = set()

    for item in relevant_items:
        metadata = item["metadata"]

        source_entry = (
            metadata["source"],
            metadata["section"],
        )

        if source_entry not in seen_sources:
            print(
                f"- {metadata['source']} - "
                f"{metadata['section']}"
            )

            seen_sources.add(source_entry)

if __name__ == "__main__":
    main()
