# tools.py — FINAL VERSION THAT WORKS (December 2025)
from typing import Any, Dict, List
from mcp_client import MCPClient


class ToolManager:
    @classmethod
    async def get_all_tools(cls, clients: dict[str, MCPClient]) -> list[dict]:
        all_declarations = []

        for client_name, client in clients.items():
            try:
                raw_tools = await client.list_tools()
                print(f"[DEBUG] Client '{client_name}' returned tools: {raw_tools}")

                # Handle both List[Tool] and plain list of dicts
                tools_list = raw_tools if isinstance(raw_tools, list) else getattr(raw_tools, "tools", [])

                for tool in tools_list:
                    try:
                        # Extract name
                        name = getattr(tool, "name", None)
                        if name is None:
                            name = tool.get("name") if isinstance(tool, dict) else "unknown_tool"

                        # Extract description
                        desc = getattr(tool, "description", "")
                        if not desc and isinstance(tool, dict):
                            desc = tool.get("description", "")

                        # Extract schema
                        schema = getattr(tool, "inputSchema", {})
                        if schema is None:
                            schema = {}
                        if hasattr(schema, "dict"):
                            schema = schema.dict()
                        elif hasattr(schema, "model_dump"):
                            schema = schema.model_dump()
                        elif isinstance(schema, dict):
                            pass
                        else:
                            schema = {}

                        # Gemini expects "parameters", not "input_schema"
                        all_declarations.append({
                            "name": name,
                            "description": str(desc),
                            "parameters": schema
                        })

                        print(f"[DEBUG] Added tool: {name}")

                    except Exception as e:
                        print(f"[DEBUG] Failed to parse one tool: {e}")

            except Exception as e:
                print(f"[DEBUG] Failed to list tools from client {client_name}: {e}")

        result = [{"function_declarations": all_declarations}] if all_declarations else []
        print(f"[DEBUG] Final tool declarations sent to Gemini: {result}")
        return result

    @classmethod
    async def execute_tool_requests(cls, clients: dict[str, MCPClient], message_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        results = []
        for call in message_data.get("tool_calls", []):
            name = call.get("name")
            args = call.get("args", {})

            client = None
            for c in clients.values():
                try:
                    tools = await c.list_tools()
                    tool_list = tools if isinstance(tools, list) else getattr(tools, "tools", [])
                    if any(getattr(t, "name", None) == name or (isinstance(t, dict) and t.get("name") == name) for t in tool_list):
                        client = c
                        break
                except:
                    continue

            if not client:
                results.append({"tool_name": name, "text": f"Tool '{name}' not found", "is_error": True})
                continue

            try:
                output = await client.call_tool(name, args)
                text = output if isinstance(output, str) else "Done"
                results.append({"tool_name": name, "text": text, "is_error": False})
            except Exception as e:
                results.append({"tool_name": name, "text": f"Error: {e}", "is_error": True})

        return results