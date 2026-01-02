# core/openai.py
import os
import json
from typing import List, Dict, Any
from openai import AsyncOpenAI
from core.llm_base import LLMServiceBase


class OpenAIService(LLMServiceBase):
    def __init__(self, model: str = "gpt-4o-mini"):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model

    async def chat(self, messages: List[Dict[str, Any]], tools=None):
        """
        Converts Anthropic-style message format → OpenAI format,
        sends the request, and returns a unified R() wrapper
        with .content (text) and .stop_reason.
        """

        # -----------------------------------------
        # Convert Anthropic-style messages to OpenAI messages
        # -----------------------------------------
        openai_messages = []
        for m in messages:
            role = m["role"]
            content = m["content"]

            # User/assistant text only
            if isinstance(content, str):
                openai_messages.append({"role": role, "content": content})
                continue

            # Handle list-of-blocks (text, tool_use, tool_result)
            blocks = []
            for block in content:
                if block["type"] == "text":
                    blocks.append(block["text"])
                elif block["type"] == "tool_use":
                    # Add tool call marker
                    blocks.append(f"[TOOL CALL REQUEST: {block['name']}]")
                elif block["type"] == "tool_result":
                    blocks.append(f"[TOOL RESULT] {block['content']}")

            joined = "\n".join(blocks) if blocks else ""
            openai_messages.append({"role": role, "content": joined})

        # -----------------------------------------
        # Convert MCP tools → OpenAI function calling format
        # -----------------------------------------
        openai_tools = None
        if tools:
            openai_tools = []
            for t in tools:
                openai_tools.append({
                    "type": "function",
                    "function": {
                        "name": t["name"],
                        "description": t.get("description", ""),
                        "parameters": t["input_schema"],  # JSON schema
                    }
                })

        # -----------------------------------------
        # Send request to OpenAI
        # -----------------------------------------
        resp = await self.client.chat.completions.create(
            model=self.model,
            messages=openai_messages,
            tools=openai_tools or None,
            temperature=0.3,
            max_tokens=2048,
        )

        choice = resp.choices[0]
        msg = choice.message

        # -----------------------------------------
        # Extract assistant TEXT (REAL FIX)
        # -----------------------------------------
        if msg.content:
            assistant_text = msg.content

        # If model made a tool call
        elif msg.tool_calls:
            # Convert tool call to JSON string for Chat to print
            assistant_text = json.dumps(
                [
                    {
                        "id": tc.id,
                        "name": tc.function.name,
                        "args": tc.function.arguments
                    }
                    for tc in msg.tool_calls
                ],
                indent=2
            )
        else:
            assistant_text = ""

        stop_reason = "tool_use" if msg.tool_calls else "end_turn"

        # -----------------------------------------
        # Wrap in unified R object for Chat class
        # -----------------------------------------
        class R:
            def __init__(self, content, stop_reason, tool_calls):
                self.content = content              # string
                self.stop_reason = stop_reason      # "tool_use" or "end_turn"
                self.tool_calls = tool_calls        # OpenAI tool call objects

        return R(
            content=assistant_text,
            stop_reason=stop_reason,
            tool_calls=msg.tool_calls,
        )

    # --------------------------------------------------------------
    # TEXT EXTRACTION — USED BY Chat.text_from_message()
    # --------------------------------------------------------------
    @staticmethod
    def text_from_message(r):
        return r.content or ""

    @staticmethod
    @staticmethod
    def to_blocks(message):
        """Convert OpenAI ChatCompletionMessage OR string into Claude-style blocks."""

        # Case 1: If model returned plain text
        if isinstance(message, str):
            return [{"type": "text", "text": message}]

        blocks = []

        # Case 2: Normal text response
        if hasattr(message, "content") and message.content:
            blocks.append({"type": "text", "text": message.content})

        # Case 3: Tool calls
        if hasattr(message, "tool_calls") and message.tool_calls:
            for tc in message.tool_calls:
                blocks.append({
                    "type": "tool_use",
                    "id": tc.id,
                    "name": tc.function.name,
                    "input": json.loads(tc.function.arguments)
                })

        return blocks
    # --------------------------------------------------------------
    # TOOL RESULT MESSAGE FORMAT
    # --------------------------------------------------------------
    @staticmethod
    def add_user_message(messages, results):
        content = []
        for r in results:
            content.append({
                "type": "tool_result",
                "tool_use_id": r.get("tool_use_id", "call_01"),
                "name": r.get("name", ""),  # important for Gemini + OpenAI
                "content": r["content"],
                "is_error": r.get("is_error", False),
            })
        messages.append({"role": "user", "content": content})
