"""
GapGPT Agent Manager
Handles intelligent model selection and task routing
"""
from typing import List, Dict
from models import query_model


def auto_select_model(prompt: str) -> str:
    """
    Automatically select the best GapGPT model based on prompt content

    Args:
        prompt: User's prompt/request

    Returns:
        Selected model name
    """
    prompt_lower = prompt.lower()

    # System and Docker tasks → GPT-5 (strongest reasoning)
    if any(keyword in prompt_lower for keyword in ["docker", "system", "container", "exec", "process"]):
        return "gpt-5"

    # Legal and formal analysis → Claude Opus 4
    if any(keyword in prompt_lower for keyword in ["legal", "contract", "document", "analysis", "review"]):
        return "claude-opus-4"

    # Image and vision tasks → Gemini 2.5 Pro
    if any(keyword in prompt_lower for keyword in ["image", "vision", "photo", "picture", "visual"]):
        return "gemini-2.5-pro"

    # Default: GPT-4o (balanced and reliable)
    return "gpt-4o"


def run_agent(prompt: str, model: str = "auto") -> Dict:
    """
    Execute agent task with intelligent model selection

    Args:
        prompt: User's request/prompt
        model: Model name or 'auto' for intelligent selection

    Returns:
        Agent response
    """
    # Auto-select model if needed
    if model == "auto":
        model = auto_select_model(prompt)

    # Prepare messages
    messages = [
        {
            "role": "system",
            "content": """You are GapGPT System Agent with FULL SYSTEM ACCESS through a backend API.

IMPORTANT CAPABILITIES:
- You CAN execute system commands via /system/run endpoint
- You CAN access Docker containers
- You CAN read/write files
- You CAN check network status
- You ARE running in a privileged Docker container

WHEN USER ASKS TO DO SOMETHING:
1. If it's a system task → you CAN do it
2. Tell user you will execute it via the API
3. Example: "I will run 'ls -la' for you" → actually executes it

NEVER say you don't have access to the system. You DO have access through the backend API.

Your responses should indicate that you can execute commands and perform system operations."""
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    # Query the model
    return query_model(model, messages)

