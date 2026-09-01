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
    arguments: dict
    reason: str

class ListProjectFilesArguments(BaseModel):
    pass

class ReadTextFileArguments(BaseModel):
    filename: str

def execute_tool(tool_name: str, arguments: dict):
    tool = TOOLS[tool_name]

    arguments_model = tool["arguments_model"]
    validated_arguments = arguments_model.model_validate(arguments)

    tool_function = tool["function"]

    return tool_function(**validated_arguments.model_dump())

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

TOOLS = {
    "list_project_files": {
        "function": list_project_files,
        "arguments_model": ListProjectFilesArguments, 
    },
    "read_text_file": {
        "function": read_text_file,
        "arguments_model": ReadTextFileArguments,
    }
}

def get_agent_decision(messages: list[dict]) -> AgentDecision:
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
    assistant_message = response_data["message"]["content"]

    return AgentDecision.model_validate_json(assistant_message)

def get_final_answer(messages: list[dict]) -> str:
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
            "content": "What files are currently in my project directory?",
        },
    ]

    decision = get_agent_decision(messages)
    print(decision)

    if decision.action == "answer":
        final_answer = get_final_answer(messages)
        print(final_answer)

    if decision.action == "use_tool":
        result = execute_tool(
            decision.tool_name,
            decision.arguments,
        )

        messages.append(
            {
                "role": "user",
                "content": (
                    f"Tool '{decision.tool_name}' returned:\n"
                    f"{result}\n\n"
                    "Answer the original request using this result."
                ),
            }
        )

        final_answer = get_final_answer(messages)
        print(final_answer)
    # elif decision.tool_name == "list_project_files":
    #     result = list_project_files()
    #     print(result)

    # elif decision.tool_name == "read_text_file":
    #     result = read_text_file(decision.tool_argument)
    #     print(result)

    

if __name__ == "__main__":
    main()