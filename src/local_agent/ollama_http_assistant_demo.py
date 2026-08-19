import requests


OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen3:8b"


def main() -> None:
    messages = [
        {
            "role": "system",
            "content": "You are a concise technical assistant."
        }, 
    ]

    # Loop for requesting user prompts
    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            break

        messages.append(
            {
                "role": "user",
                "content": user_input
            }
        )

        # Build an Ollama request body
        request_body = {
            "model": MODEL_NAME,
            "messages": messages,
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
        assistant_message = response_data["message"]["content"]

        print(f"Assistant: {assistant_message}")

        messages.append(
            {
                "role": "assistant",
                "content": assistant_message,
            }
        )

if __name__ == "__main__":
    main()