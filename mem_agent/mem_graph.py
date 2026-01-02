
from mem0 import Memory
from dotenv import load_dotenv
import os
from openai import OpenAI
from qdrant_client import QdrantClient
import json

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI()
# BASIC WORKING CONFIG FOR REMOTE QDRANT CLOUD
config = {
    "version": "v1.1",
    "vector_store": {
        "provider": "qdrant",
        "config": {
            # "url": "remoteurl",
            # "api_key": os.getenv("QDRANT_API_KEY"),
            "host": "localhost",
             "port": 6333,
            "collection_name": "localhost_memorytest2026" # fixed name → visible in dashboard
        }
    },
    "embedder": {
        "provider": "openai",
        "config": {
            "model": "text-embedding-3-small",
            "api_key": os.getenv("OPENAI_API_KEY")
        }
    },
    "llm": {  # any cheap model works
        "provider": "openai",
        "config": {
            "model": "gpt-4o-mini",
            "api_key": os.getenv("OPENAI_API_KEY")
        }
    },
    "graph_store":{
        "provider":"neo4j",
        "config":{
            "url":"neo4j+s://f3bbfba6.databases.neo4j.io",
            "username":"neo4j",
            "password":"f1r5nHTcryEfiP-IRcGnnl89n78JiuVOAocb4WwV4Ww"
        }
    }
}
mem_client = Memory.from_config(config)
# print("client testing ...")
# test_client = QdrantClient(
#     url="remoteurl",
#     api_key=os.getenv("QDRANT_API_KEY"),
#     prefer_grpc=True
# )

# print("Connected to Qdrant Cloud!")
# print("Current collections:", [c.name for c in test_client.get_collections().collections])
while True:

    user_query = input(">")
    
    search_memory = mem_client.search(query=user_query,user_id="jenish")

    memories = [
        f"ID:{mem.get("id")}\nMemory:{mem.get("memory")}" for mem in search_memory.get("results")
    ]
    
    print("Found memories",memories)
    SYSTEM_PROMPT = f"""
    Here is the context about the user:
    {json.dumps(memories)}
"""
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role":"system","content":SYSTEM_PROMPT},
            {"role": "user","content":user_query}
        ]
    )
    ai_response = response.choices[0].message.content

    print("AI:",ai_response)

    mem_client.add(
        user_id="jenish",
        messages=[
            {
                "role":"user","content":user_query
            },
            {
                "role":"assistant",
                "content":ai_response
            }
        ]
    )
    print("Memory has been saved")

