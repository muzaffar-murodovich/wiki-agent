#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
cli.py - Terminal entry point for wiki-agent.

A REPL-style chat: type a request in natural language, the agent decides which
tools to use. "Write" actions (e.g. publishing) ask for y/n confirmation.

Usage:
    python cli.py                 # interactive chat
    python cli.py "Avicenna maqolasini o'zbekchaga tarjima qil"   # one-shot
"""

import os
import sys

os.environ.setdefault("PYWIKIBOT_NO_USER_CONFIG", "2")

from dotenv import load_dotenv  # noqa: E402

load_dotenv(override=True)

import config  # noqa: E402
from agent import Agent  # noqa: E402
from utils.logger import logger  # noqa: E402


def confirm(tool_name: str, arguments: dict) -> bool:
    """Ask the user to approve a write action (human-in-the-loop)."""
    print(f"\n⚠️  Agent '{tool_name}' amalini bajarmoqchi:")
    for k, v in arguments.items():
        preview = str(v)
        if len(preview) > 400:
            preview = preview[:400] + " …"
        print(f"   {k}: {preview}")
    answer = input("Tasdiqlaysizmi? [y/N]: ").strip().lower()
    return answer in ("y", "yes", "ha", "ha'")


def _check_keys() -> bool:
    if config.AGENT_PROVIDER == "openai" or config.TRANSLATION_PROVIDER == "openai":
        if not config.OPENAI_API_KEY:
            logger.fail("OPENAI_API_KEY topilmadi. .env faylga qo'shing.")
            return False
    return True


def main():
    if not _check_keys():
        sys.exit(1)

    agent = Agent(confirm=confirm)

    logger.section("🤖 wiki-agent — oʻzbekcha Vikipediya yordamchisi")
    print("Buyruq yozing (chiqish uchun 'exit' yoki Ctrl+C).\n")

    # One-shot mode if a prompt was passed as arguments.
    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
        print(f"› {user_input}\n")
        reply = agent.send(user_input)
        print(f"\n{reply}\n")
        return

    while True:
        try:
            user_input = input("› ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit", "chiqish"):
            break
        reply = agent.send(user_input)
        print(f"\n{reply}\n")

    logger.info("Xayr! 👋")


if __name__ == "__main__":
    main()
