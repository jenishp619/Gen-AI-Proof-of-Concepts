import asyncio
import sys
import os
from dotenv import load_dotenv
from contextlib import AsyncExitStack

from mcp_client import MCPClient
from core.claude import Claude
from google import genai
from core.cli_chat import CliChat
from core.cli import CliApp

load_dotenv()

# Anthropic Config
gemini_model = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-0")
gemini_api_key = os.getenv("GEMINI_API_KEY", "")

assert gemini_model, "gemini-2.5-flash"
import asyncio
import sys
import os
from dotenv import load_dotenv
from contextlib import AsyncExitStack
from typing import Dict, Any, List # Add typing imports

# Remove Anthropic-specific imports
# from core.claude import Claude 
# from google import genai # Remove this, we'll import GeminiService instead

from mcp_client import MCPClient
from core.cli_chat import CliChat
from core.cli import CliApp

# --- NEW: Import the GeminiService wrapper ---
# Adjust the import path if gemini.py is not in the 'core' directory
from core.gemini import GeminiService 

load_dotenv()

# Gemini Config
# Using GEMINI_MODEL from env or defaulting to gemini-1.5-flash
gemini_model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash") 
gemini_api_key = os.getenv("GEMINI_API_KEY", "")

assert gemini_model_name, "GEMINI_MODEL environment variable must be set."
assert gemini_api_key, "Error: GEMINI_API_KEY cannot be empty. Update .env"


async def main():
    # --- NEW: Instantiate the GeminiService wrapper ---
    gemini_service = GeminiService(api_key=gemini_api_key, model_name=gemini_model_name)

    # Get root directories from command line arguments
    root_paths = sys.argv[1:]
    if not root_paths:
        print("Usage: python main.py <root1> [root2] ...")
        print("Example: python main.py /path/to/videos /another/path")
        sys.exit(1)

    clients = {} 

    async with AsyncExitStack() as stack:
        # Create the MCP client with the provided root directories
        doc_client = await stack.enter_async_context(
            MCPClient(
                command=sys.executable,  # Using sys.executable is safer than "python"
                args=["mcp_server.py"], 
                roots=root_paths,
            )
        )
        clients["doc_client"] = doc_client

        # Pass the new gemini_service instance to CliChat
        chat = CliChat(
            doc_client=doc_client,
            clients=clients,
            gemini_service=gemini_service, # Pass the GeminiService wrapper here
        )

        cli = CliApp(chat)
        await cli.initialize()
        await cli.run()


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy()) 
    asyncio.run(main())
assert gemini_api_key, (
    "Error: GEMINI_API_KEY cannot be empty. Update .env"
)


async def main():
    gemini_service = genai.Client(api_key=gemini_api_key)

    # Get root directories from command line arguments
    root_paths = sys.argv[1:]
    if not root_paths:
        print("Usage: python main.py <root1> [root2] ...")
        print("Example: python main.py /path/to/videos /another/path")
        sys.exit(1)

    clients = {} # This dict might be used for other services if you expand

    async with AsyncExitStack() as stack:
        # Create the MCP client with the provided root directories
        doc_client = await stack.enter_async_context(
            MCPClient(
                command="python",  # Use current python executable
                args=["mcp_server.py"], 
                roots=root_paths,
            )
        )
        clients["doc_client"] = doc_client

        # Pass the new gemini_service instance to CliChat
        chat = CliChat(
            doc_client=doc_client,
            clients=clients,
            gemini_service=gemini_service, # Pass the Gemini service here
        )

        cli = CliApp(chat)
        await cli.initialize()
        await cli.run()


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy()) 
    asyncio.run(main())