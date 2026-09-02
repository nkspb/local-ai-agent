"""
A module for determining which tools exist,
how their arguments are validated,
and how the tools are executed
"""


from pathlib import Path

from .schemas import (
    ListProjectFilesArguments,
    ReadTextFileArguments,
)

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

def execute_tool(tool_name: str, arguments: dict):
    if tool_name not in TOOLS:
        raise ValueError(f"Unknown tool: {tool_name}")
    
    tool = TOOLS[tool_name]

    arguments_model = tool["arguments_model"]
    validated_arguments = arguments_model.model_validate(arguments)

    tool_function = tool["function"]

    return tool_function(**validated_arguments.model_dump())