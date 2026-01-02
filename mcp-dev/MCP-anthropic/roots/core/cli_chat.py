from typing import List, Dict, Any
from mcp.types import Prompt, PromptMessage
from core.chat import Chat
from mcp_client import MCPClient
from core.gemini import GeminiService 

class CliChat(Chat):
    def __init__(
        self,
        doc_client: MCPClient,
        clients: dict[str, MCPClient],
        gemini_service: GeminiService, 
    ):
        super().__init__(gemini_service=gemini_service, clients=clients)

        self.doc_client: MCPClient = doc_client

    async def list_prompts(self) -> list[Prompt]:
        return await self.doc_client.list_prompts()

    async def get_prompt(
        self, command: str, doc_id: str
    ) -> list[PromptMessage]:
        return await self.doc_client.get_prompt(command, {"doc_id": doc_id})

    # Note: _process_query is already defined in Chat.
    # Overriding it here is fine if you just want to call super(), 
    # but strictly speaking not needed if logic is identical.
    async def _process_query(self, query: str):
         await super()._process_query(query)

# Helpers for prompts (kept as is)
def convert_prompt_message_to_gemini_format(prompt_message: "PromptMessage") -> Dict[str, Any]:
    role = "model" if prompt_message.role == "assistant" else "user"
    content = prompt_message.content

    if hasattr(content, "type") and content.type == "text":
        return {"role": role, "content": content.text}
    if isinstance(content, str):
        return {"role": role, "content": content}
    if isinstance(content, list):
        text_parts = []
        for item in content:
            if hasattr(item, "type") and item.type == "text":
                text_parts.append(item.text)
            elif isinstance(item, str):
                text_parts.append(item)
        if text_parts:
            return {"role": role, "content": "\n".join(text_parts)}
            
    return {"role": role, "content": str(content)}

def convert_prompt_messages_to_gemini_format(prompt_messages: List[PromptMessage]) -> List[Dict[str, Any]]:
    return [convert_prompt_message_to_gemini_format(msg) for msg in prompt_messages]