from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from prompt_toolkit.history import InMemoryHistory
from core.cli_chat import CliChat
from typing import Dict, Any, List
import json
from pyboxen import boxen
import asyncio # Added for potential async operations if needed

# Gemini's streaming events are not directly exposed like Claude's
# We'll need to adapt CliChat's 'run' method to yield/callback with a more generic
# event structure if streaming is desired, or process the full response.

class CliApp:
    def __init__(self, agent: CliChat):
        self.agent = agent
        self.history = InMemoryHistory()
        self.session = PromptSession(
            history=self.history,
            style=Style.from_dict(
                {
                    "prompt": "#aaaaaa",
                    "completion-menu.completion": "bg:#222222 #ffffff",
                    "completion-menu.completion.current": "bg:#444444 #ffffff",
                }
            ),
            complete_while_typing=True,
            complete_in_thread=True,
        )

    async def initialize(self):
        pass

    async def run(self):
        while True:
            try:
                user_input = await self.session.prompt_async("> ")
                if not user_input.strip():
                    continue

                print()

                # --- NEW: Adapt the event handling for Gemini ---
                # Gemini's streaming is different. Instead of low-level Anthropic events,
                # CliChat's `run` method (which calls `gemini_service.chat_stream`)
                # needs to yield/callback with structured info (text, tool_calls).

                # For simplicity, let's assume CliChat.run will yield full text chunks
                # and fully formed tool calls for now.

                # If CliChat.run needs to *stream* partial tool calls, it would look
                # significantly different and GeminiService would need to yield
                # the raw streaming chunks for parsing here.
                # For this example, we'll aim for a simpler callback where CliChat
                # pre-parses stream and only sends complete text or tool calls.

                # Let's redefine `handle_event` to expect more processed data from CliChat.
                # This implies CliChat.run will have to do more work to interpret Gemini's stream.
                
                # --- This will be the new state to build up streamed responses/tool_calls ---
                current_response_text = ""
                # Maps index to {'name': str, 'args': dict}
                current_tool_calls: Dict[int, Dict[str, Any]] = {} 

                # The `on_event` callback from CliChat.run will now receive more structured events.
                async def handle_processed_event(event_data: Dict[str, Any]):
                    nonlocal current_response_text
                    nonlocal current_tool_calls

                    event_type = event_data.get("type")

                    if event_type == "text_chunk":
                        text_chunk = event_data.get("text")
                        if text_chunk:
                            current_response_text += text_chunk
                            print(text_chunk, end="", flush=True)
                    elif event_type == "tool_call":
                        # This implies CliChat has already parsed the full tool call from Gemini's stream
                        tool_name = event_data["name"]
                        tool_args = event_data["args"]
                        tool_index = event_data.get("index", len(current_tool_calls)) # Assign index if not provided

                        current_tool_calls[tool_index] = {
                            "name": tool_name,
                            "args": tool_args,
                        }
                        
                        print() # New line before tool call box

                        try:
                            formatted_args = json.dumps(tool_args, indent=2)
                            tool_content = f"🔧 {tool_name}\n\nArguments:\n{formatted_args}"
                        except (json.JSONDecodeError, TypeError, ValueError):
                            tool_content = f"🔧 {tool_name}\n\nArguments: {tool_args}"

                        tool_box = boxen(
                            tool_content,
                            title="Tool Call",
                            style="rounded",
                            color="blue",
                            padding=0,
                        )
                        print(tool_box)
                        # Immediately remove after printing if we assume CliChat handles execution
                        if tool_index in current_tool_calls:
                            del current_tool_calls[tool_index] 
                    # Add other event types if CliChat sends them (e.g., "tool_result", "end_of_stream")

                # The CliChat.run method now needs to be modified to process Gemini's stream
                # and call `handle_processed_event` with structured dictionaries.
                # This is the biggest conceptual shift.
                await self.agent.run(
                    user_input, stream=True, on_event=handle_processed_event # Pass the new handler
                )

                print() # Add newline after everything

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"\nAn error occurred: {e}")
                # For debugging, print full traceback:
                # import traceback
                # traceback.print_exc()