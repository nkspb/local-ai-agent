import json
import requests

from typing import Literal
from pydantic import BaseModel, ValidationError
from pathlib import Path

OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen3:8b"

MAX_AGENT_STEPS = 5

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
    if tool_name not in TOOLS:
        raise ValueError(f"Unknown tool: {tool_name}")
    
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
    user_input = input("You: ")

    messages = [
        {
            "role": "system",
            "content": (
                "You are an assistent that can use tools.\n"
                "Available tools:\n"
                "- list_project_files: List files and directories "
                "in the current project directory.\n"
                "- read_text_file: Reads the contents of a text file in the current"
                "project directory. Requires filename.\n\n"
                "Its tool_argument must contain the filename.\n\n"
                "Use tools when local information is required. "
                "When you have enough information, choose action='answer'."
            ),
        },
        {
            "role": "user",
            "content": user_input,
        },
    ]

    for step in range(MAX_AGENT_STEPS):
        

        try:
            decision = get_agent_decision(messages)
            print(f"Step {step + 1}: {decision.action}")
        except ValidationError as error:
            print(f"Invalid agent decision: {error}")
            return
       
        if decision.action == "answer":
            final_answer = get_final_answer(messages)
            print(f"Assistant: {final_answer}")
            return

        try:
            result = execute_tool(
                decision.tool_name,
                decision.arguments,
            )
            observation = (
                f"Tool '{decision.tool_name}' returned:\n"
                f"{result}"
            )

        except (ValidationError, ValueError, OSError) as error:
            observation = (
                f"Tool '{decision.tool_name}' failed:\n"
                f"{error}"
            )
            

        messages.append(
            {
                "role": "user",
                "content": (
                    f"{observation}\n\n"
                    "Use this information when deciding the next action."
                ),
            }
        )

    print("Agent stopped because it reached the maximum number of steps.")
    
    # elif decision.tool_name == "list_project_files":
    #     result = list_project_files()
    #     print(result)

    # elif decision.tool_name == "read_text_file":
    #     result = read_text_file(decision.tool_argument)
    #     print(result)

    

if __name__ == "__main__":
    main()