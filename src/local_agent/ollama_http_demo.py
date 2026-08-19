import requests


OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen3:8b"


def main() -> None:
    # Build an Ollama request body
    request_body = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": "You are a concise technical assistant."
            }, 
            {
                "role": "user",
                "content": "Explain what Ollama does in one sentence."
            },
        ],
        "stream": False,
    }
    # Send a request
    response = requests.post(
        OLLAMA_CHAT_URL,
        json=request_body,
        timeout=120,
    )

    response.raise_for_status()

    # Print the response
    response_data = response.json()
    print(response_data)
    assistant_message = response_data["message"]["content"]

    print(assistant_message)

if __name__ == "__main__":
    main()