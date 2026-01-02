# cli_chat.py
from typing import List, Tuple
from mcp.types import Prompt, PromptMessage
from core.gemini import Gemini          # ← our Gemini class
from mcp_client import MCPClient
from core.chat import Chat


class CliChat(Chat):
    def __init__(
        self,
        doc_client: MCPClient,
        clients: dict[str, MCPClient],
        claude_service: Gemini,         # ← type hint fixed
    ):
        super().__init__(gemini_service=claude_service, clients=clients)  # ← pass as gemini_service
        self.doc_client: MCPClient = doc_client

    async def list_prompts(self) -> list[Prompt]:
        return await self.doc_client.list_prompts()

    async def list_docs_ids(self) -> list[str]:
        return await self.doc_client.read_resource("docs://documents")

    async def get_doc_content(self, doc_id: str) -> str:
        return await self.doc_client.read_resource(f"docs://documents/{doc_id}")

    async def get_prompt(self, command: str, doc_id: str) -> list[PromptMessage]:
        return await self.doc_client.get_prompt(command, {"doc_id": doc_id})

    async def _extract_resources(self, query: str) -> str:
        mentions = [word[1:] for word in query.split() if word.startswith("@")]
        if not mentions:
            return ""

        doc_ids = await self.list_docs_ids()
        mentioned_docs: List[Tuple[str, str]] = []

        for doc_id in doc_ids:
            if doc_id in mentions:
                content = await self.get_doc_content(doc_id)
                mentioned_docs.append((doc_id, content))

        return "".join(
            f'\n<document id="{doc_id}">\n{content}\n</document>\n'
            for doc_id, content in mentioned_docs
        )

    async def _process_command(self, query: str) -> bool:
        if not query.startswith("/"):
            return False

        parts = query.strip().split(maxsplit=2)
        if len(parts) < 2:
            return False

        command = parts[0][1:]      # remove the "/"
        doc_id = parts[1]

        try:
            messages = await self.doc_client.get_prompt(command, {"doc_id": doc_id})
        except Exception as e:
            print(f"Warning: Failed to load prompt /{command}: {e}")
            return True

        # Convert PromptMessage → Gemini message format (simple text blocks)
        for msg in messages:
            content = msg.content
            if isinstance(content, str):
                text = content
            elif isinstance(content, list):
                text = " ".join(item.text for item in content if hasattr(item, "text"))
            else:
                text = str(content)

            self.messages.append({
                "role": "user" if msg.role == "user" else "assistant",
                "content": text
            })
        return True

    async def _process_query(self, query: str):
        if await self._process_command(query):
            return

        added_resources = await self._extract_resources(query)

        prompt = f"""
            The user has a question:
        <query>
        {query}
        </query>

        The following context may be useful:
        <context>
        {added_resources}
        </context>

        Answer directly and concisely. Do not mention the context or tools unless asked.
        """.strip()

        self.messages.append({"role": "user", "content": prompt})