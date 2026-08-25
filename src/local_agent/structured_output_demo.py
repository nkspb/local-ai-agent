import json
import requests

OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen3:8b"

def send_chat_request(messages: list[dict]) -> str:
    request_body = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False,
    }

    response = requests.post(
        OLLAMA_CHAT_URL,
        json=request_body,
        timeout=120,
    )

    response.raise_for_status()
    response_data = response.json()
    return response_data["message"]["content"]


def main() -> None:
    messages = [
        {
            "role": "system",
            "content": (
                "You are a technical assistant. "
                "Always answer using valid JSON with exactly these fields: "
                '"topic" and "difficulty". '
                'The difficulty must be one of: "beginner", "intermediate", "advanced".'
            ),
        },
        {
            "role": "user",
            "content": "Explain the difficulty level of Kubernetes networking."
        },
    ]

    assistant_message = send_chat_request(messages)

    print("Raw response:")
    print(assistant_message)

    parsed_response = json.loads(assistant_message)

    print()
    print("Parsed topic:")
    print(parsed_response["topic"])

    print("Parsed difficulty:")
    print(parsed_response["difficulty"])

if __name__ == "__main__":
    main()