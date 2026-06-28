#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
agent/loop.py - Agentic tool-use loop.

Drives a conversation with the AGENT-role provider. On each turn the model may
request tool calls; the loop executes them via the tool registry, feeds results
back, and repeats until the model returns a final text answer (or the iteration
cap is hit). "Write" tools pause for human confirmation before executing.
"""

import json
from typing import Callable, Dict, List, Optional

import config
import tools
from providers import get_provider
from utils.logger import logger

# confirm(tool_name, arguments) -> bool
ConfirmFn = Callable[[str, Dict], bool]


class Agent:
    """Stateful agent that holds a conversation and dispatches tools."""

    def __init__(self, confirm: Optional[ConfirmFn] = None):
        self.provider = get_provider(config.AGENT_PROVIDER)
        self.model = config.AGENT_MODEL
        self.confirm = confirm or (lambda name, args: True)
        self.messages: List[Dict] = []
        logger.info(f"🧭 Agent provayderi: {self.provider.name} ({self.model})")

    def send(self, user_message: str) -> str:
        """Process one user message, returning the agent's final text reply."""
        self.messages.append({"role": "user", "content": user_message})

        for _ in range(config.AGENT_MAX_ITERATIONS):
            response = self.provider.complete(
                messages=self.messages,
                model=self.model,
                tools=tools.SCHEMAS,
                system=config.AGENT_SYSTEM_PROMPT,
            )

            # Record the assistant turn (rebuilt in canonical OpenAI format).
            assistant_msg: Dict = {"role": "assistant", "content": response.content}
            if response.has_tool_calls:
                assistant_msg["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.name, "arguments": json.dumps(tc.arguments)},
                    }
                    for tc in response.tool_calls
                ]
            self.messages.append(assistant_msg)

            if not response.has_tool_calls:
                return response.content or ""

            # Execute each requested tool and append its result.
            for tc in response.tool_calls:
                result = self._run_tool(tc.name, tc.arguments)
                self.messages.append(
                    {"role": "tool", "tool_call_id": tc.id, "content": result}
                )

        logger.warning("Agent iteratsiya chegarasiga yetdi.")
        return "⚠️ Vazifa juda koʻp qadam talab qildi — toʻxtatildi. Iltimos, soʻrovni soddalashtiring."

    def _run_tool(self, name: str, arguments: Dict) -> str:
        logger.info(f"🔧 Vosita chaqirilmoqda: {name}")
        if name in tools.WRITE_TOOLS:
            if not self.confirm(name, arguments):
                logger.warning(f"Foydalanuvchi rad etdi: {name}")
                return "BEKOR QILINDI: foydalanuvchi bu amalni tasdiqlamadi."
        return tools.dispatch(name, arguments)
