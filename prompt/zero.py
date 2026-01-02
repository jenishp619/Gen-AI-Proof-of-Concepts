from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()

client = OpenAI(api_key=os.getenv("GEMINI_API_KEY"),base_url="https://generativelanguage.googleapis.com/v1beta/openai/")

# zero shot prompt: directly giving instruction to the model
SYSTEM_PROMPT = "you should only answer coding related questions only. If user asks something other than coding then just say sorry i can help with coding tasks you name is AI"
response = client.chat.completions.create(model="gemini-2.5-flash",
                                          messages=[
                                              {"role":"system","content":SYSTEM_PROMPT},
                                              {"role":"user","content":"Hello there can you TELL ME A joke for coding"},
                                          ])

print(response.choices[0].message.content)
# Zero shot prompting - The model is given direct question or task without prior examples
