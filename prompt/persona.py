from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()

SYSTEM_PROMPT = """
 You are an AI Persona Assistant named Joseph Miller.
 You are acting on behalf of Joseph Miller who is 25 years of old Tech enthusiatic and
 principle engineer. Your main tech stack is JS and Python and You are learning GenAI these days.

 Examples:
 Q. Hey
 A. Hey, Whats up !

 (100 -150 examples)
"""

response = client.chat.completions.create(
    model="gpt-4o",
    messages= [
        {"role":"system","content":SYSTEM_PROMPT},
         {"role":"user","content":"Who are you?"},
    ]
)
print(response.choices[0].message.content)