from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()

client = OpenAI(api_key=os.getenv("GEMINI_API_KEY"),base_url="https://generativelanguage.googleapis.com/v1beta/openai/")

# few shot prompt: directly giving instruction to the model and few examples to the model.
SYSTEM_PROMPT = """you should only answer coding related questions only. If user asks something other than coding then just say sorry i can help with coding tasks you name is AI

Rule:
- Strictly follow the output in JSON format

Output Format:
{{
 "code": "string or none,
 "isCodingquestion": boolean
}}
EXAMPLES:
Q: Can you explain the a+b square?
A: {{"code":null,"isCodingquestion":false}}

Q: Hey, Write a code in python for adding two numbers
A:  {{"code":"def  add(a,b):return a+b","isCodingquestion":true}}
"""
response = client.chat.completions.create(model="gemini-2.5-flash",
                                          messages=[
                                              {"role":"system","content":SYSTEM_PROMPT},
                                              {"role":"user","content":"Hello there can you explain pythagoras code"},
                                          ])

print(response.choices[0].message.content)
# Few shot prompting - The model is provided with a few examples before asking it to generate a response.
