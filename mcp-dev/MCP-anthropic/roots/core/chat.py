import asyncio
from typing import List, Dict, Any, Union

# Adjust this import to match your project structure
# If gemini.py is inside the 'core' folder, use:
from core.gemini import GeminiService 
from mcp_client import MCPClient
from core.tools import ToolManager


class Chat:
    def __init__(
        self, 
        gemini_service: GeminiService, 
        clients: dict[str, MCPClient],
    ):
        self.gemini_service: GeminiService = gemini_service
        self.clients: dict[str, MCPClient] = clients
        self.messages: List[Dict[str, Any]] = []

    # --- Helper methods ---
    def _add_assistant_message(self, messages: List[Dict[str, Any]], response: Dict[str, Any]):
        """Adds an assistant message (text or tool_calls) to the messages list."""
        if "text" in response and response["text"]:
            messages.append({"role": "model", "content": response["text"]})
        elif "tool_calls" in response and response["tool_calls"]:
            messages.append({"role": "model", "tool_calls": response["tool_calls"]})
        else:
            # Only print warning if truly empty (Gemini sometimes sends empty chunks)
            pass

    def _add_user_message(self, messages: List[Dict[str, Any]], tool_results: List[Dict[str, Any]]):
        parts = []
        for result in tool_results:
            name = result["tool_name"]
            text = result["text"]
            is_error = result.get("is_error", False)

            response = {"output": text}
            if is_error:
                response = {"error": text}

            parts.append({
                "function_response": {
                    "name": name,
                    "response": response
                }
            })

        if parts:
            messages.append({"role": "user", "parts": parts})

    def _text_from_message(self, response: Dict[str, Any]) -> str:
        if "text" in response:
            return response["text"]
        return ""

    async def _process_query(self, query: str):
        self.messages.append({"role": "user", "content": query})

    

    async def run(
    self,
    query: str,
    stream: bool = False,
    on_event=None,
    ) -> str:
        final_text_response = ""
        await self._process_query(query)

        while True:
            # Load tools
            gemini_tools_config = []
            try:
                raw_tools = await ToolManager.get_all_tools(self.clients)
                if raw_tools:
                    gemini_tools_config = raw_tools  # ← Already perfect format
                print(f"[DEBUG] Tools loaded for Gemini: {len(gemini_tools_config)} tool groups")
            except Exception as e:
                print(f"Warning: Could not load tools: {e}")

            # Call Gemini
            if stream and on_event:
                current_tool_calls = []

                async for event_data in self.gemini_service.chat_stream(
                    messages=self.messages,
                    tools=gemini_tools_config,
                ):
                    if event_data["type"] == "text_chunk":
                        text = event_data["text"]
                        final_text_response += text
                        await on_event(event_data)
                    elif event_data["type"] == "tool_call":
                        current_tool_calls.append(event_data)
                        await on_event(event_data)

                # === CRITICAL FIX: Handle tool calls ===
                if current_tool_calls:
                    # Add tool call to history
                    self.messages.append({
                        "role": "model",
                        "tool_calls": current_tool_calls
                    })

                    # Execute tools
                    try:
                        tool_results = await ToolManager.execute_tool_requests(
                            self.clients, {"tool_calls": current_tool_calls}
                        )
                        self._add_user_message(self.messages, tool_results)

                        # Send tool results back to user in CLI
                        for result in tool_results:
                            text = result["text"]
                            if result.get("is_error"):
                                print(f"\nError: {text}")
                            else:
                                print(f"\n{text}")

                        # Reset and continue to get Gemini's final response
                        final_text_response = ""
                        continue  # This triggers another Gemini call with tool result
                    except Exception as e:
                        print(f"Tool execution error: {e}")
                        break

                # No tool calls → final response
                if final_text_response.strip():
                    self._add_assistant_message(self.messages, {"text": final_text_response})
                break

            else:  # Non-streaming (already correct)
                response = await self.gemini_service.chat(
                    messages=self.messages,
                    tools=gemini_tools_config,
                )
                self._add_assistant_message(self.messages, response)

                if response.get("tool_calls"):
                    tool_results = await ToolManager.execute_tool_requests(self.clients, response)
                    self._add_user_message(self.messages, tool_results)
                    continue
                else:
                    final_text_response = response.get("text", "")
                    break

        return final_text_response