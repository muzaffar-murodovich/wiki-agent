#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
providers/openai_provider.py - OpenAI implementation of LLMProvider.
"""

import json
from typing import Any, Dict, List, Optional

from openai import OpenAI

from providers.base import LLMProvider, LLMResponse, ToolCall


class OpenAIProvider(LLMProvider):
    """LLM provider backed by the OpenAI Chat Completions API."""

    name = "openai"

    def __init__(self, api_key: Optional[str] = None):
        self.client = OpenAI(api_key=api_key)

    def complete(
        self,
        messages: List[Dict[str, Any]],
        model: str,
        tools: Optional[List[Dict[str, Any]]] = None,
        system: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> LLMResponse:
        full_messages: List[Dict[str, Any]] = []
        if system:
            full_messages.append({"role": "system", "content": system})
        full_messages.extend(messages)

        kwargs: Dict[str, Any] = {"model": model, "messages": full_messages}
        if tools:
            kwargs["tools"] = tools
        if temperature is not None:
            kwargs["temperature"] = temperature

        response = self.client.chat.completions.create(**kwargs)
        message = response.choices[0].message

        tool_calls: List[ToolCall] = []
        for tc in message.tool_calls or []:
            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}
            tool_calls.append(ToolCall(id=tc.id, name=tc.function.name, arguments=args))

        usage: Dict[str, int] = {}
        if getattr(response, "usage", None):
            usage["total_tokens"] = response.usage.total_tokens
            usage["prompt_tokens"] = response.usage.prompt_tokens
            details = getattr(response.usage, "prompt_tokens_details", None)
            usage["cached_tokens"] = getattr(details, "cached_tokens", 0) if details else 0

        return LLMResponse(content=message.content, tool_calls=tool_calls, usage=usage)
