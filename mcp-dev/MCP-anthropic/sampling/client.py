import asyncio
import os
import sys
from google import genai
from google.genai import types
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.session import RequestContext
from mcp.types import (
    CreateMessageRequestParams,
    CreateMessageResult,
    TextContent,
    SamplingMessage,
)
api_key = "#######"
print("API-key",api_key)
client = genai.Client(api_key=api_key)

MODEL_ID = "gemini-2.5-flash"

server_params = StdioServerParameters(
    command= "python", # Or "python" depending on how you run it
    args=["server.py"],
)

async def sampling_callback(
    context: RequestContext, params: CreateMessageRequestParams
):
    # 1. Convert MCP Messages to Gemini Content objects
    gemini_contents = []
    
    for msg in params.messages:
        role = "model" if msg.role == "assistant" else "user"
        
        # Handle TextContent vs plain text
        text_content = ""
        if hasattr(msg.content, "text"):
            text_content = msg.content.text
        else:
            text_content = str(msg.content)

        gemini_contents.append(
            types.Content(
                role=role,
                # FIX: Instantiate types.Part directly
                parts=[types.Part(text=text_content)] 
            )
        )

    # 2. Configure generation parameters
    # Note: Use getattr to safely get camelCase attributes (maxTokens) 
    max_tokens = getattr(params, "maxTokens", 1000) 
    sys_prompt = getattr(params, "systemPrompt", None)

    config = types.GenerateContentConfig(
        max_output_tokens=max_tokens,
        temperature=params.temperature if params.temperature else 1.0,
        system_instruction=sys_prompt 
    )

    # 3. Call Gemini
    response = await client.aio.models.generate_content(
        model=MODEL_ID, 
        contents=gemini_contents,
        config=config,
    )

    # 4. Return result
    return CreateMessageResult(
        role="assistant",
        model=MODEL_ID,
        content=TextContent(type="text", text=response.text),
    )

async def run():
    # 'async with' handles closing the client automatically
    async with genai.Client(api_key=api_key).aio as client:
        
        async def sampling_callback(context: RequestContext, params: CreateMessageRequestParams):
            print("\n  [⚡ SAMPLING START] Server has paused and is asking CLIENT for help!")
            print(f"  [👀 CHECK] Server says: 'Please complete this prompt for me...'")
            gemini_contents = []
            
            for msg in params.messages:
                role = "model" if msg.role == "assistant" else "user"
                text_content = msg.content.text if hasattr(msg.content, "text") else str(msg.content)

                gemini_contents.append(
                    types.Content(
                        role=role,
                        parts=[types.Part(text=text_content)]
                    )
                )

            max_tokens = getattr(params, "maxTokens", 1000) 
            my_custom_prompt = "You are an expert researcher. Provide detailed, academic, and well-structured summaries."
            print(f"  [🤖 CONFIG] Enforcing System Prompt: '{my_custom_prompt}'")
            sys_prompt = getattr(params, "systemPrompt", None)

            config = types.GenerateContentConfig(
                max_output_tokens=max_tokens,
                temperature=params.temperature if params.temperature else 1.0,
                system_instruction=my_custom_prompt 
            )

            print(f"  [🤖 ACTION] Client is now calling Gemini {MODEL_ID}...")
            response = await client.models.generate_content(
                model=MODEL_ID,
                contents=gemini_contents,
                config=config,
            )

            print("  [✅ SUCCESS] Gemini finished. Sending answer BACK to Server.")
            print("  [⚡ SAMPLING END] Resuming Server execution...\n")
            
            return CreateMessageResult(
                role="assistant",
                model=MODEL_ID,
                content=TextContent(type="text", text=response.text),
            )

        # Connect to MCP Server
        print("Connecting to server...")
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(
                read, write, sampling_callback=sampling_callback
            ) as session:
                await session.initialize()
                print("✅ Connected! System ready.")
                print("---------------------------------------------------------")
                # print(f"Calling tool 'summarize' on server using {MODEL_ID}...")

                while True:

                    try:
                        user_input = await asyncio.to_thread(input,"\n📝 Enter topic/text to summarize (or 'q' to quit):")
                    except EOFError:
                        break

                    if user_input.lower() in ["q","quit","exit"]:
                        print("Goodbye")
                        break
                    if not user_input.strip():
                        continue

                    print("Sending to server")


                    try:
                       
                        result = await session.call_tool(
                            name="summarize",
                            arguments={"text_to_summarize": user_input},
                        )
                        
                        print("\n--- 🤖 Server Summary ---")
                        # The result comes back as a list of content blocks
                        for content in result.content:
                            print(content.text)
                        print("---------------------------------------------------------")
                        
                    except Exception as e:
                        print(f"❌ Error calling tool: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(run())
    except Exception as e:
        print(f"\n❌ Error: {e}")


# async def run():
#     async with stdio_client(server_params) as (read, write):
#         async with ClientSession(
#             read, write, sampling_callback=sampling_callback
#         ) as session:
#             await session.initialize()

#             # Call the tool on the server
#             # The server will pause, call back to our 'sampling_callback', 
#             # wait for Gemini's answer, and then finish the tool execution.
#             print(f"Calling tool 'summarize' on server using {MODEL_ID}...")
            
#             result = await session.call_tool(
#                 name="summarize",
#                 arguments={"text_to_summarize": "Gemini 1.5 Flash is a lightweight, fast, and cost-efficient model designed for high-frequency tasks."},
#             )
            
#             # This output comes from the Server (after it got the answer from our Client)
#             print("\n--- Result from Server ---")
#             print(result.content[0].text)

# if __name__ == "__main__":
#     asyncio.run(run())