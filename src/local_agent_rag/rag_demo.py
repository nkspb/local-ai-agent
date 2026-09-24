import requests
import chromadb

from embedding_demo import get_embedding

OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
CHAT_MODEL = "qwen3:8b"

# We need to send the current prompt combined with the history
# to LLM, therefore two arguments for question and context

# A system prompt is stable, while user message is constantly updated
def ask_llm(question: str, context: str) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                "You are a technical assistant. "
                "Answer the user's question using only the provided context."
                "If the context does not contain enough information, say so"
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
    # print(f"[DEBUG] response_data:\n=============={response_data}\n==============\n\n")
    return response_data["message"]["content"]

def main() -> None:
    # Initialize an in-memory chromadb client for development
    client = chromadb.Client()

    # Create an initial collection to put our embedded chunks into
    collection = client.create_collection(
        name="devops_docs"
    )

    documents = [
        "Kubernetes Services provide stable network access to Pods.",
        "Deployments manage ReplicaSets and application rollouts.",
        "Chocolate cake tastes better with coffee.",
    ]

    ids = [
        "doc1",
        "doc2",
        "doc3",
    ]

    # Now that we have prepared documents, we need to embed them to vectors
    # which will be stored in ChromaDB and later used for semantic search
    embeddings = [
        get_embedding(document)
        for document in documents
    ]

    # We now save our documents along their embeddings and ids
    # Original text is a must because there's no way to deduce real words from embeddings
    # ids is a built-in collection field
    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
    )

    questions = [
        "How can I give Pods a stable network endpoint?",
        "How do Kubernetes Deployments manage rollouts?",
        "How does Istio mTLS work?",
        "What is the best chocolate cake recipe?",
    ]

    # We embed the prompt to then use it for semantic search
    # We have only one embedding, while Chroma can accept more
    query_embeddings = [get_embedding(question) for question in questions]

    results = collection.query(
        query_embeddings=query_embeddings,
        n_results=2,
        include=[
            "documents",
            "distances",
        ],
    )

    # print(f"[DEBUG] results:\n=============={results}\n==============\n\n")

    for question, retrieved_documents, retrieved_distances in zip (
        questions,
        results["documents"],
        results["distances"],
    ):
        print(f"Question: {question}")

        # Next is to build context to augment a request to LLM with,
        # which will be used to construct a reply to the user
        context = "\n\n".join(retrieved_documents)

        answer = ask_llm(
            question=question,
            context=context
        )

        # print("Retrieved documents:")
        # for document in retrieved_documents:
        #     print(f"- {document}")
        for document, distance in zip(
            retrieved_documents,
            retrieved_distances,
        ):
            print(f"Distance: {distance}")
            print(f"Document: {document}")
            print()

        print()
        print("Answer:")
        print(answer)

if __name__ == "__main__":
    main()