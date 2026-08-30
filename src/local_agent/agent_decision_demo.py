import json
import requests

from typing import Literal
from pydantic import BaseModel
from pathlib import Path

OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen3:8b"

class AgentDecision(BaseModel):
    action: Literal["answer", "use_tool"]
    reason: str

def list_project_files() -> list[str]:
    project_dir = Path.cwd()

    return [
        item.name
        for item in project_dir.iterdir()
    ]

def send_chat_request(messages: list[dict]) -> str:
    request_body = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False,
        "format": AgentDecision.model_json_schema()
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
                "You are an assistent that decides how to handle a user request. "
                "Choose 'answer' if the request can be answered using general knowledge. "
                "Choose 'use_tool' if the request requires information from the user's "
                "local computer or environment."
            ),
        },
        {
            "role": "user",
            "content": "What is a docker container?",
        },
    ]

    assistant_message = send_chat_request(messages)
    parsed_response = json.loads(assistant_message)

    decision = AgentDecision.model_validate(parsed_response)

    if decision.action == "answer":
        print("The model decided it can answer directly.")

    elif decision.action == "use_tool":
        files = list_project_files()

        print("Tool result:")
        print(files)

    print(decision)

if __name__ == "__main__":
    main()