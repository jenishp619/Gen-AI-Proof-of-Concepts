# tools.py — FIXED for Gemini validation
import json
from typing import List, Dict, Any, Optional
from mcp.types import CallToolResult, Tool, TextContent
from mcp_client import MCPClient

class ToolManager:
    @classmethod
    async def get_all_tools(cls, clients: dict[str, MCPClient]) -> list[dict]:
        tools = []
        for client in clients.values():
            try:
                tool_models = await client.list_tools()
                for t in tool_models:
                    tools.append({
                        "name": t.name,
                        "description": t.description or "",
                        "input_schema": t.inputSchema,
                    })
            except Exception as e:
                print(f"Warning: Failed to list tools: {e}")
        return tools

    @classmethod
    async def _find_client_with_tool(cls, clients: List[MCPClient], tool_name: str) -> Optional[MCPClient]:
        for client in clients:
            try:
                tools = await client.list_tools()
                if any(t.name == tool_name for t in tools):
                    return client
            except Exception:
                continue
        return None

    @classmethod
    async def execute_tool_requests(cls, clients: dict[str, MCPClient], gemini_response) -> List[Dict[str, Any]]:
        if not gemini_response.content or not gemini_response.content.parts:
            return []

        tool_results = []

        for part in gemini_response.content.parts:
            if not hasattr(part, "function_call") or not part.function_call:
                continue

            tool_name = part.function_call.name
            tool_input = dict(part.function_call.args)
            tool_use_id = "call_01"  # Gemini doesn't provide, so we fake

            client = await cls._find_client_with_tool(list(clients.values()), tool_name)

            if not client:
                result_content = json.dumps({"error": f"Tool '{tool_name}' not found"})
                is_error = True
            else:
                try:
                    result: CallToolResult = await client.call_tool(tool_name, tool_input)
                    texts = [
                        item.text for item in result.content
                        if isinstance(item, TextContent)
                    ] if result and result.content else ["<no output>"]
                    result_content = json.dumps(texts if texts else [""])
                    is_error = bool(result.isError) if result else False
                except Exception as e:
                    result_content = json.dumps({"error": str(e)})
                    is_error = True

            # FIXED: Always include tool name (Gemini requires it!)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool_use_id,
                "name": tool_name,  # ← THIS WAS MISSING! Critical for Gemini validation
                "content": result_content,
                "is_error": is_error,
            })

        return tool_results