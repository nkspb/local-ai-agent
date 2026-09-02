"""
A module for the orchestration layer
"""
from pydantic import ValidationError

from .ollama_client import (
    get_agent_decision,
    get_final_answer,
)
from .tools import execute_tool

MAX_AGENT_STEPS = 5

def run_agent(user_input: str) -> str:
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

    for _ in range(MAX_AGENT_STEPS):
        try:
            decision = get_agent_decision(messages)
        except ValidationError as error:
            return f"Invalid agent decision: {error}"
            
       
        if decision.action == "answer":
            return get_final_answer(messages)

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