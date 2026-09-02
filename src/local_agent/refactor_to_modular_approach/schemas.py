"""
A module for determining which shapes of data are valid
"""
from typing import Literal

from pydantic import BaseModel

class AgentDecision(BaseModel):
    action: Literal["answer", "use_tool"]
    tool_name: Literal["list_project_files", "read_text_file", "none"]
    arguments: dict
    reason: str

class ListProjectFilesArguments(BaseModel):
    pass

class ReadTextFileArguments(BaseModel):
    filename: str