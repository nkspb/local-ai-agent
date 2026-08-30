import json
import requests

from typing import Literal
from pydantic import BaseModel
from pathlib import Path

OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen3:8b"

class AgentDecision(BaseModel):
    action: Literal["answer", "use_tool"]
    tool_name: Literal["list_project_files", "read_text_file", "none"]
    tool_argument: str | None
    reason: str

def list_project_files() -> list[str]:
    project_dir = Path.cwd()

    return [
        item.name
        for item in project_dir.iterdir()
    ]

def read_text_file(filename: str) -> str:
    project_dir = Path.cwd()
    file_path = project_dir / filename

    return file_path.read_text(encoding="utf-8")

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
                "You are an assistent that decides how to handle a user request.\n\n"
                "Available tools:\n"
                "- list_project_files: List files and directories in the current project directory. "
                "It requires no argument.\n"
                "- read_text_file: Reads the contents of a text file in the current project directory. "
                "Its tool_argument must contain the filename.\n\n"
                "Choose 'answer' if the request can be answered using general knowledge.\n"
                "Choose 'use_tool' if local project information is required.\n"
                "If action is 'anwer', set tool_name to 'none' and tool_argument to null."
            ),
        },
        {
            "role": "user",
            "content": "What is a Kubernetes Service?",
        },
    ]

    assistant_message = send_chat_request(messages)
    parsed_response = json.loads(assistant_message)

    decision = AgentDecision.model_validate(parsed_response)
    print(decision)

    if decision.action == "answer":
        print("The model decided it can answer directly.")

    elif decision.tool_name == "list_project_files":
        result = list_project_files()
        print(result)

    elif decision.tool_name == "read_text_file":
        result = read_text_file(decision.tool_argument)
        print(result)

    

if __name__ == "__main__":
    main()