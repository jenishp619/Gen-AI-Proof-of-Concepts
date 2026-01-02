# main.py
import asyncio
import sys
import os
from dotenv import load_dotenv
from contextlib import AsyncExitStack

from mcp_client import MCPClient
from core.gemini import Gemini  # ← Now using Gemini!

from core.cli_chat import CliChat
from core.cli import CliApp

load_dotenv()

# === CONFIG ===
gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")  # or gemini-2.5-pro
gemini_api_key = os.getenv("GEMINI_API_KEY")

assert gemini_api_key, "Error: GEMINI_API_KEY not found in .env file!"

async def main():
    # Use Gemini instead of Claude
    gemini_service = Gemini(model=gemini_model)

    server_scripts = sys.argv[1:]
    clients = {}

    command, args = (
        ("uv", ["run", "mcp_server.py"])
        if os.getenv("USE_UV", "0") == "1"
        else ("python", ["mcp_server.py"])
    )

    async with AsyncExitStack() as stack:
        doc_client = await stack.enter_async_context(
            MCPClient(command=command, args=args)
        )
        clients["doc_client"] = doc_client

        for i, server_script in enumerate(server_scripts):
            client_id = f"client_{i}_{server_script}"
            client = await stack.enter_async_context(
                MCPClient(command="uv", args=["run", server_script])
            )
            clients[client_id] = client

        # Pass Gemini service instead of Claude
        chat = CliChat(
            doc_client=doc_client,
            clients=clients,
            claude_service=gemini_service,  # ← same interface expected!
        )

        cli = CliApp(chat)
        await cli.initialize()
        await cli.run()


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    asyncio.run(main())