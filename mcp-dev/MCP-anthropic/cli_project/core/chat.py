# chat.py
from core.gemini import Gemini  # ← Changed import
from mcp_client import MCPClient
from core.tools import ToolManager
from typing import List, Dict


class Chat:
    def __init__(self, gemini_service: Gemini, clients: dict[str, MCPClient]):
        self.gemini_service: Gemini = gemini_service
        self.clients = clients
        self.messages: List[Dict] = []  # same format as before

    async def _process_query(self, query: str):
        self.messages.append({"role": "user", "content": query})

    async def run(self, query: str) -> str:
        final_text_response = ""

        await self._process_query(query)

        while True:
            response = await self.gemini_service.chat(
                messages=self.messages,
                tools=await ToolManager.get_all_tools(self.clients),
            )

            Gemini.add_assistant_message(self.messages, response)

            if response.stop_reason == "tool_use":
                print(Gemini.text_from_message(response))
                tool_result_parts = await ToolManager.execute_tool_requests(
                    self.clients, response
                )
                Gemini.add_user_message(self.messages, tool_result_parts)
            else:
                final_text_response = Gemini.text_from_message(response)
                break

        return final_text_response