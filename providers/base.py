#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
providers/base.py - LLM provider abstraction.

Defines a provider-agnostic interface so the agent loop and the translation
pipeline do not depend on any single vendor. The MVP ships an OpenAI provider;
future providers (Anthropic, DeepSeek, Mistral, Qwen) implement the same ABC.

Design note: the canonical message format is the OpenAI chat format
(list of {"role", "content", ...} dicts, plus tool messages). New providers
translate this format internally. Responses are normalized into `LLMResponse`.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ToolCall:
    """A single tool/function call requested by the model."""
    id: str
    name: str
    arguments: Dict[str, Any]


@dataclass
class LLMResponse:
    """Normalized response from any provider."""
    content: Optional[str]
    tool_calls: List[ToolCall] = field(default_factory=list)
    usage: Dict[str, int] = field(default_factory=dict)

    @property
    def has_tool_calls(self) -> bool:
        return bool(self.tool_calls)


class LLMProvider(ABC):
    """Provider-agnostic chat interface."""

    name: str = "base"

    @abstractmethod
    def complete(
        self,
        messages: List[Dict[str, Any]],
        model: str,
        tools: Optional[List[Dict[str, Any]]] = None,
        system: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> LLMResponse:
        """
        Send a chat completion request.

        Args:
            messages: Conversation in OpenAI chat format.
            model: Model id to use for this call.
            tools: Optional list of tool schemas (OpenAI function-tool format).
            system: Optional system prompt prepended to the conversation.
            temperature: Optional sampling temperature.

        Returns:
            A normalized LLMResponse (content and/or tool_calls).
        """
        raise NotImplementedError
