import os
from google import genai
# Added FunctionCall and FunctionResponse to types for safer object creation
from google.genai.types import (
    GenerateContentConfig, 
    Tool, 
    FunctionDeclaration, 
    Content, 
    Part, 
    FunctionCall, 
    FunctionResponse
)
from typing import List, Dict, Any

class Gemini:
    def __init__(self, model: str = "gemini-2.0-flash"):
        # Updated default to 2.0-flash as 2.5 is not yet standard public syntax 
        # (unless you have specific preview access, keep your 2.5)
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not set!")

        self.client = genai.Client(api_key=api_key)
        self.model_name = model

    async def chat(self, messages: List[Dict[str, Any]], tools: List[Dict] | None = None):
        # 1. Convert messages to SDK Content objects
        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            content = msg["content"]

            if isinstance(content, str):
                parts = [Part(text=content)]
            else:
                parts = []
                for block in content:
                    if block.get("type") == "text":
                        parts.append(Part(text=block["text"]))
                    elif block.get("type") == "tool_use":
                        # Explicitly use FunctionCall object
                        parts.append(Part(
                            function_call=FunctionCall(
                                name=block["name"], 
                                args=block["input"]
                            )
                        ))
                    elif block.get("type") == "tool_result":
                        # Explicitly use FunctionResponse object
                        parts.append(Part(
                            function_response=FunctionResponse(
                                name=block.get("name", ""), 
                                response={"result": block["content"]}
                            )
                        ))
                if not parts:
                    parts = [Part(text="")]

            contents.append(Content(role=role, parts=parts))

        # 2. Configure Tools
        gemini_tools = None
        if tools:
            declarations = [
                FunctionDeclaration(
                    name=t["name"], 
                    description=t.get("description", ""), 
                    parameters=t["input_schema"]
                )
                for t in tools
            ]
            gemini_tools = [Tool(function_declarations=declarations)]

        config = GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=8192,
            tools=gemini_tools,
        )

        # 3. OFFICIAL ASYNC PATTERN (Corrected)
        # client.aio is not a context manager. Call it directly.
        response = await self.client.aio.models.generate_content(
            model=self.model_name,
            contents=contents,
            config=config,
        )

        # Wrapper to match your MCP server structure
        class FakeResponse:
            def __init__(self, r):
                self.content = r.candidates[0].content if r.candidates else None
                # Detect stop reason based on presence of function calls
                self.stop_reason = "tool_use" if self.content and any(p.function_call for p in self.content.parts if p.function_call) else "end_turn"

        return FakeResponse(response)

    @staticmethod
    def text_from_message(r):
        if not r.content: return ""
        return "".join(p.text for p in r.content.parts if p.text)

    @staticmethod
    def add_assistant_message(messages, r):
        if not r.content: return
        blocks = []
        for p in r.content.parts:
            if p.text:
                blocks.append({"type": "text", "text": p.text})
            elif p.function_call:
                fc = p.function_call
                # Ensure args are converted to dict if they aren't already
                args = fc.args if isinstance(fc.args, dict) else dict(fc.args)
                blocks.append({"type": "tool_use", "id": "call_01", "name": fc.name, "input": args})
        
        if blocks:
            messages.append({"role": "assistant", "content": blocks})

    @staticmethod
    def add_user_message(messages, results):
        content = [
            {
                "type": "tool_result",
                "tool_use_id": r.get("tool_use_id", "call_01"),
                "content": str(r["content"]), # Ensure content is stringified for safety
                "is_error": r.get("is_error", False),
                "name": r.get("name") # Pass name back if available
            }
            for r in results
        ]
        messages.append({"role": "user", "content": content})