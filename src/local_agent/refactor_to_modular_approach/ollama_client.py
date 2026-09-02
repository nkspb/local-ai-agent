"""
A module for determining how to talk to Ollama.
"""
import requests

from .schemas import AgentDecision

OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen3:8b"

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