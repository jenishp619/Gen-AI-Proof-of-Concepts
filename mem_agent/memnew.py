
import os
from mem0 import Memory
from dotenv import load_dotenv

load_dotenv()

# BASIC WORKING CONFIG FOR REMOTE QDRANT CLOUD
config = {
    "version": "v1.1",
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "url": "remoteurl",
            "api_key": os.getenv("QDRANT_API_KEY"),
            "collection_name": "jenish_memory_2025" # fixed name → visible in dashboard
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
    }
}

# This is the line that finally forces a single visible collection
m = Memory.from_config(config)
messages = [
    {"role": "user", "content": "I'm planning to watch a movie tonight. Any recommendations?"},
    {"role": "assistant", "content": "How about thriller movies? They can be quite engaging."},
    {"role": "user", "content": "I’m not a big fan of thriller movies but I love sci-fi movies."},
    {"role": "assistant", "content": "Got it! I'll avoid thriller recommendations and suggest sci-fi movies in the future."}
]
# Store something
m.add(
    messages,
    user_id="jenish",
    metadata={"category": "movies"}
)

print("Memory saved! Go to Qdrant Cloud → you will now see collection:")
print("   jenish_memory_2025")