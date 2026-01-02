# core/gemini.py
import os
from google import genai
from google.genai import types
from typing import Dict, Any, List, AsyncGenerator

class GeminiService:
    def __init__(self, api_key: str, model_name: str):
        self._genai_client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def _convert_messages_to_gemini_content(self, messages: List[Dict[str, Any]]) -> List[types.Content]:
        gemini_contents = []
        for msg in messages:
            role = "model" if msg["role"] == "assistant" or msg["role"] == "model" else "user"
            parts = []

            if "content" in msg:
                if isinstance(msg["content"], str) and msg["content"]:
                    parts.append(types.Part(text=msg["content"]))
                elif isinstance(msg["content"], list):
                    for item in msg["content"]:
                        if isinstance(item, dict) and "text" in item:
                            parts.append(types.Part(text=item["text"]))

            if role == "model" and "tool_calls" in msg and msg["tool_calls"]:
                for tool_call_data in msg["tool_calls"]:
                    parts.append(types.Part(
                        function_call=types.FunctionCall(
                            name=tool_call_data["name"],
                            args=tool_call_data["args"]
                        )
                    ))

            if role == "user" and "parts" in msg:
                for part_data in msg["parts"]:
                    if "function_response" in part_data:
                        func_resp = part_data["function_response"]
                        resp_content = func_resp["response"]
                        if not isinstance(resp_content, dict):
                            resp_content = {"output": str(resp_content)}
                            
                        parts.append(types.Part(
                            function_response=types.FunctionResponse(
                                name=func_resp["name"],
                                response=resp_content
                            )
                        ))

            if parts: 
                 gemini_contents.append(types.Content(role=role, parts=parts))

        return gemini_contents

    def _parse_gemini_response(self, response) -> Dict[str, Any]:
        response_dict = {"text": "", "tool_calls": [], "stop_reason": "stop"}

        if hasattr(response, 'text') and response.text:
            response_dict["text"] = response.text
        
        if hasattr(response, 'candidates') and response.candidates:
            first_candidate = response.candidates[0]
            if first_candidate.content and first_candidate.content.parts:
                for part in first_candidate.content.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        response_dict["tool_calls"].append({
                            "name": part.function_call.name,
                            "args": dict(part.function_call.args)
                        })
                        response_dict["stop_reason"] = "tool_code"
                    
                    if hasattr(part, 'text') and part.text and not response_dict["text"]:
                        response_dict["text"] += part.text

            if first_candidate.finish_reason:
                if first_candidate.finish_reason == "STOP":
                    response_dict["stop_reason"] = "stop"
                elif first_candidate.finish_reason == "MAX_TOKENS":
                    response_dict["stop_reason"] = "max_tokens"

        return response_dict

    def _build_tool_config(self, tools: List[Dict[str, Any]]):
        if not tools:
            return None
        
        function_declarations = []
        for tool_decl in tools:
            if "function_declarations" in tool_decl:
                for func_decl_data in tool_decl["function_declarations"]:
                    function_declarations.append(
                        types.FunctionDeclaration(
                            name=func_decl_data["name"],
                            description=func_decl_data.get("description", ""),
                            parameters=func_decl_data.get("parameters", {})
                        )
                    )
        
        if not function_declarations:
            return None
            
        return types.Tool(function_declarations=function_declarations)

    # --- Non-streaming chat ---
    async def chat(
        self,
        messages: List[Dict[str, Any]],
        system_instruction: str = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        tools: List[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        
        gemini_contents = self._convert_messages_to_gemini_content(messages)
        tool_config = self._build_tool_config(tools)

        config = types.GenerateContentConfig(
            max_output_tokens=max_tokens,
            temperature=temperature,
            system_instruction=system_instruction,
            tools=[tool_config] if tool_config else None,
        )

        async with self._genai_client.aio as aio_client:
            response = await aio_client.models.generate_content(
                model=self.model_name,
                contents=gemini_contents,
                config=config, 
            )
        
        return self._parse_gemini_response(response)

    # --- Streaming chat ---
    async def chat_stream(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]] = None,
        system_instruction: str = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> AsyncGenerator[Dict[str, Any], None]: 
        
        gemini_contents = self._convert_messages_to_gemini_content(messages)
        tool_config = self._build_tool_config(tools)

        config = types.GenerateContentConfig(
            max_output_tokens=max_tokens,
            temperature=temperature,
            system_instruction=system_instruction,
            tools=[tool_config] if tool_config else None,
        )

        async with self._genai_client.aio as aio_client:
            # FIX: Use generate_content_stream, remove stream=True
            stream_response = await aio_client.models.generate_content_stream(
                model=self.model_name,
                contents=gemini_contents,
                config=config,
            )
            
            async for chunk in stream_response:
                if chunk.text:
                    yield {"type": "text_chunk", "text": chunk.text}
                
                if chunk.candidates:
                    for candidate in chunk.candidates:
                        if candidate.content and candidate.content.parts:
                            for part in candidate.content.parts:
                                if hasattr(part, 'function_call') and part.function_call:
                                    yield {
                                        "type": "tool_call",
                                        "name": part.function_call.name,
                                        "args": dict(part.function_call.args),
                                        "index": 0 
                                    }