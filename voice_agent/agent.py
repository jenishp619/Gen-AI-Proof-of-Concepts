import os
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI
import json
import requests
from pydantic import BaseModel,Field
from openai import AsyncOpenAI
from openai.helpers import LocalAudioPlayer
import speech_recognition as sr
import asyncio
load_dotenv()

client = OpenAI()
async_client = AsyncOpenAI()

async def tts(speech:str):
    async with async_client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
         voice="coral",
        input=speech,
        instructions="Always Speak in a cheerful manner with full of delight and happy.",
        response_format="pcm",
    ) as response:
        await LocalAudioPlayer().play(response)
        

def run_command(cmd:str):
    result = os.system(cmd)
    return result

def get_weather(city:str):
    url = f"https://wttr.in/{city.lower()}?format=%C+%t"
    response = requests.get(url)

    if response.status_code == 200:
        return f"The weather in {city} is {response.text}"
    
    return "Something went wrong"

available_tools = {
    "get_weather": get_weather,
    "run_command":run_command,
}
# chain of thought: 
SYSTEM_PROMPT = """
 You are an expert AI assistant in resolving user queries using chain of thought.
 You work on START, PLAN and OUTPUT steps.
 You need to first PLAN what needs to be done. The PLAN can be multiple steps.
 Once you think enough PLAN has been done, finally you can give an OUTPUT.
 You can also call a tool if required from the list of available tools.
 for every tool call wait for the observe step which is the output from the 
 RULES:
 - Strictly follow the given JSON output format
 - Only run one step at a time
 - The sequence of steps is START (where user gives an input), PLAN(that can be multiple times) and finally OUTPUT(which is going to be displayed to the user).

 Output JSON format:
 {"step":"START" | "PLAN" | "OUTPUT" | "TOOL", "content":"string","tool":"string","input":"string"}

 Available Tools:
 - get_weather(city:str): Takes city name as input string and returns the weather info about the city.
 - run_command(cmd:str): Takes a system linux command as string and execute the command on user system and return the output from that command
 
 Example:

 Example 1:
 START: Hey, Can you solve 2+ 3 * 5 / 10
 PLAN: {"step":"PLAN","content":"Seems like user is interested in math problem"}
 PLAN: {"step":"PLAN","content":"looking at the problem, we should solve using BODMAS method"}
 PLAN: {"step":"PLAN","content":"Yes the BODMAS is correct thing to be done here"}
 PLAN: {"step":"PLAN","content":"first we multiply 3 * 5 which is 15"}
 PLAN: {"step":"PLAN","content":"Now the new equation is 2 + 15 / 10"}
 PLAN: {"step":"PLAN","content":"We must perform divide that is 15 / 10"}
 PLAN: {"step":"PLAN","content":"Now finally lets perform the add 3.5"}
 PLAN: {"step":"PLAN","content":"Great, we have solved and finally left with 3.5 as answer"}
 OUTPUT: {"step":"OUTPUT","content":"3.5"}

 Example 2:
 START: What is the weather of Halifax?
 PLAN: {"step":"PLAN","content":"Seems like user is interested in weather of halifax in Canada"}
 PLAN: {"step":"PLAN","content":"Lets see if we have any available tool from the list of available tools"}
 PLAN: {"step":"PLAN","content":"Great, we have  get_weather tool available for this query"}
 PLAN: {"step":"PLAN","content":"I need to call get_weather tool for halifax input for the city"}
 PLAN: {"step":"TOOL","tool":"get_weather","input":"halifax"}
 PLAN: {"step":"OBSERVE","tool":"get_weather","output":"The weather in halifax is Light rain +12°C"}
 PLAN: {"step":"PLAN","content":"Great, I got the weather info about halifax"}
 OUTPUT: {"step":"OUTPUT","content":"The current weather in halifax is 12 C with some cloud sky"}
"""

class MyOutputFormat(BaseModel):
    step: str = Field(...,description="The ID of the step. Example: PLAN,OUTPUT,TOOL,etc")
    content: Optional[str] = Field(None, description="The optional string content for the step ")
    tool: Optional[str] = Field(None,description="The ID of the tool to call =")
    input: Optional[str] = Field(None,description="The input parameters for the tool")
    

message_history = [
    {"role":"system","content":SYSTEM_PROMPT}
]

r = sr.Recognizer()
with sr.Microphone() as source: #Mic access
    r.adjust_for_ambient_noise(source) # cut
    r.pause_threshold = 2 
    while True:
        print("Speak something...")
        audio = r.listen(source)
        user_input = r.recognize_google(audio)

           
        message_history.append({"role":"user","content":user_input})

        while True:
            # response = client.chat.completions.create(model="gpt-4o", response_format={"type":"json_object"}, messages=message_history)
            response = client.chat.completions.parse(model="gpt-4.1",
                                                    response_format=MyOutputFormat,
                                                    messages=message_history)
            #  raw result is in json format 
            raw_result = response.choices[0].message.content
            message_history.append({"role":"assistant","content":raw_result})
            #  converting the json format into python object here
            # parsed_result = json.loads(raw_result)
            parsed_result = response.choices[0].message.parsed
            if parsed_result.step == "START":
                print("🎉",parsed_result.content)
                continue

            if parsed_result.step == "TOOL":
                tool_to_call = parsed_result.tool
                tool_input = parsed_result.input
                print(f"🔪🔪:{tool_to_call} ({tool_input})")
                tool_response = available_tools[tool_to_call](tool_input)
                print(f"🔪🔪:{tool_to_call} ({tool_input})={tool_response}")

                message_history.append({"role":"developer","content":json.dumps(
                    {
                        "step":"OBSERVE","tool":tool_to_call,"input":tool_input,"output":tool_response
                    }
                )})
                continue

            if parsed_result.step == "PLAN":
                print("🧠",parsed_result.content)
                continue

            if parsed_result.step == "OUTPUT":
                print("🤖",parsed_result.content)
                asyncio.run(tts(speech=parsed_result.content))
                break


