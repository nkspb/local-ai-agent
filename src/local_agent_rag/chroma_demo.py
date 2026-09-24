import chromadb

from embedding_demo import get_embedding

def main() -> None:
    client = chromadb.Client() # in memory client

    collection = client.create_collection( # similar to a table
        name="devops_docs"
    )

    documents = [
        "Kubernetes Services provide stable network access to Pods.",
        "Deployments manage ReplicaSets and application rollouts.",
        "Chocolate cake tastes better with coffee.",
    ]

    # Is it a must to provide ids?
    ids = [
        "doc1",
        "doc2",
        "doc3",
    ]

    # Does it mean here we get just one vector as if this is a user prompt
    # Like it is not as if chunks were embedded
    embeddings = [
        get_embedding(document)
        for document in documents
    ]

    # Is not collections id column generated automatically?
    # And it is called ids here (like randomly) - how does chroma knows it is an id?
    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
    )

    query = "How can I give Pods a stable network endpoint?"

    query_embedding = get_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=2,
    )

    print(results)

if __name__ == "__main__":
    main()