"""LLM integration layer for IBM watsonx.ai Granite models."""

from .client import GraniteLLMClient
from .prompts import PromptTemplate, SystemPrompts

__all__ = ["GraniteLLMClient", "PromptTemplate", "SystemPrompts"]

# Made with Bob
