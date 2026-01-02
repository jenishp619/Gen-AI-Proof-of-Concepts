from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()

client = OpenAI(api_key=os.getenv("GEMINI_API_KEY"),base_url="https://generativelanguage.googleapis.com/v1beta/openai/")


response = client.chat.completions.create(model="gemini-2.5-flash",
                                          messages=[
                                              {"role":"system","content":"You are an expert in maths and only and only answer maths related question"},
                                              {"role":"user","content":"Hello there can you write a program for fibonacii series"},
                                          ])

print(response.choices[0].message.content)