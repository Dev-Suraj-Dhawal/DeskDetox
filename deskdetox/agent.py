"""Antigravity Agent Configuration for DeskDetox.

Configures the Agent with Google Studio API (gemini-1.5-flash),
system instructions, and open data sensory tools.
"""

import os
from typing import Optional, List, Callable, Any
from dotenv import load_dotenv

from deskdetox.tools import get_location, get_weather, get_nearby_nature

# Load environment variables from .env file
load_dotenv()

SYSTEM_INSTRUCTIONS = (
    "You are an outdoor micro-adventure guide. Your goal is to get the user away from all screens. "
    "Use your tools to find their location, weather, and nearby green spaces. Based on how much time they have, "
    "generate a highly specific, actionable 2-sentence mission for them to go outside RIGHT NOW. "
    "The mission must be phone-free. Do not output fluff, just the mission."
)


# Deprecated or retired models that should be mapped to the current active flash model
DEPRECATED_MODELS = {
    "gemini-1.5-flash": "gemini-3.8-flash",
    "gemini-1.5-pro": "gemini-3.1-pro-preview",
    "gemini-2.0-flash": "gemini-3.8-flash",
    "gemini-2.5-flash": "gemini-3.8-flash",
}


def get_api_key() -> Optional[str]:
    """Retrieve the Gemini / Google Studio API key from environment variables."""
    return os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")


def resolve_model(requested_model: Optional[str] = None) -> str:
    """Resolve the active model, handling environment overrides and deprecated identifiers.

    Args:
        requested_model: Specifically requested model name.

    Returns:
        str: Validated active Gemini model name.
    """
    model_name = requested_model or os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
    return DEPRECATED_MODELS.get(model_name, model_name)


def build_agent_config(
    api_key: Optional[str] = None,
    tools: Optional[List[Callable[..., Any]]] = None,
    model: Optional[str] = None,
) -> Any:
    """Construct the LocalAgentConfig for the Antigravity Agent.

    Args:
        api_key: Google AI Studio API key. If omitted, fetched from .env.
        tools: List of tool functions to provide to the agent.
        model: Gemini model identifier (defaults to GEMINI_MODEL or gemini-3.8-flash).

    Returns:
        LocalAgentConfig: The configured agent settings.
    """
    from google.antigravity import LocalAgentConfig

    active_api_key = api_key or get_api_key()
    if active_api_key:
        os.environ["GEMINI_API_KEY"] = active_api_key
        os.environ["GOOGLE_API_KEY"] = active_api_key

    active_model = resolve_model(model)
    tool_list = tools if tools is not None else [get_location, get_weather, get_nearby_nature]

    # Initialize LocalAgentConfig with system instructions and tools
    config_kwargs = {
        "system_instructions": SYSTEM_INSTRUCTIONS,
        "tools": tool_list,
    }

    # Pass api_key and model if supported by config kwargs
    if active_api_key:
        try:
            return LocalAgentConfig(api_key=active_api_key, model=active_model, **config_kwargs)
        except TypeError:
            pass

    try:
        return LocalAgentConfig(model=active_model, **config_kwargs)
    except TypeError:
        return LocalAgentConfig(**config_kwargs)
