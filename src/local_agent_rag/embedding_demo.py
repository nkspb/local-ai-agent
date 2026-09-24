import requests
import math

OLLAMA_EMBED_URL= "http://localhost:11434/api/embed"
EMBEDDING_MODEL = "nomic-embed-text:latest"

def get_embedding(text: str) -> list[float]:
    request_body = {
        "model": EMBEDDING_MODEL,
        "input": text,
    }

    response = requests.post(
        OLLAMA_EMBED_URL,
        json=request_body,
        timeout=120,
    )

    response.raise_for_status()

    response_data = response.json()
    # print(f"response.json(): {response_data}")
          
    return response_data["embeddings"][0]

def main() -> None:
    text = "Kubernetes Services provide stable network access to Pods."

    embedding = get_embedding(text)

    print(f"Embedding length: {len(embedding)}")
    print("First 10 values:")
    print(embedding[:10])

    # Test embeddings
    text_a = "Kubernetes Services provide stable network access to Pods."
    text_b = "How can I give Pods a stable network endpoint?"
    text_c = "Chocolate cake tastes better with coffee."

    embedding_a = get_embedding(text_a)
    embedding_b = get_embedding(text_b)
    embedding_c = get_embedding(text_c)

    print(
        "A vs B:",
        cosine_similarity(embedding_a, embedding_b)
    )

    print(
        "A vs C:",
        cosine_similarity(embedding_a, embedding_c)
    )


def cosine_similarity(vector_a: list[float], vector_b: list[float]) -> float:
    # zip combines similarly positioned numbers
    # and then they are multiplied and summed together,
    # which is what dot product is
    dot_product = sum(
        a * b
        for a, b in zip(vector_a, vector_b)
    )

    # Using the Pythagorean theorem, we calculate the length of the vector
    # y2 = a2 + b2
    magnitude_a = math.sqrt(
        sum(a * a for a in vector_a)
    )

    magnitude_b = math.sqrt(
        sum(b * b for b in vector_b)
    )

    return dot_product / (magnitude_a * magnitude_b)

if __name__ == "__main__":
    main()
