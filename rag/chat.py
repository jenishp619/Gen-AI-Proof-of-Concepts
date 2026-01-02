from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from openai import OpenAI
load_dotenv()

openai_client = OpenAI()
#  creating vector embeddings from the chunks
embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-large"
)

vector_db = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="learning_rag",
    embedding=embedding_model,
)
# Take user input
user_query = input("Ask something")

# similarity search on vector db 
# relevant chunks from the vector db 

search_results = vector_db.similarity_search(query=user_query)
# we can also control the number of chunks return using the K parameter in similarity search(k=4) , this will result in top 4 chunks
print(f"Number of chunks retreived :{len(search_results)}")
context = "\n\n\n".join([f"Page Content:{result.page_content}\nPage Number: {result.metadata['page_label']}\nFile Location:{result.metadata['source']}" for result in search_results])

SYSTEM_PROMPT = f"""
You are helpful AI assistant who answers user query based on the available context
retreived from a PDF file along with page_contents and page number

You should only ans the user based on the following contezt and navigate the user to open
the right page number to know more.

Context:
{context}
"""

response = openai_client.chat.completions.create(
    model="gpt-5",
    messages= [
        {"role":"system","content":SYSTEM_PROMPT},
        {"role":"user","content":user_query}
    ]
)

print(f"🤖🤖:{response.choices[0].message.content}")