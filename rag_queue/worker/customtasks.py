# queue/customtasks.py
from worker.celery_app import app
from openai import OpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from dotenv import load_dotenv

load_dotenv()                   

# -------------------------------------------------
# OpenAI & Qdrant clients (created once per worker)
# -------------------------------------------------
openai_client = OpenAI()
embedding_model = OpenAIEmbeddings(model="text-embedding-3-large")

vector_db = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="learning_rag",
    embedding=embedding_model,
)

# -------------------------------------------------
# Celery task
# -------------------------------------------------
@app.task(bind=True)
def process_query(self, query: str) -> str:
    print(f"[Celery] Processing query: {query}")

    # 1. Retrieve relevant chunks
    results = vector_db.similarity_search(query=query, k=4)

    # 2. Build context string
    context_lines = [
        f"Page {r.metadata.get('page_label', '?')}: {r.page_content}"
        for r in results
    ]
    context = "\n\n".join(context_lines)

    # 3. Prompt + OpenAI call
    system_prompt = f"""You are a helpful assistant. Answer **only** using the context below.
    If the answer cannot be derived from the context, say "I don't know".

    Context:
    {context}
    """

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ],
        temperature=0.3,
    )
    answer = response.choices[0].message.content
    print(f"[Celery] Answer: {answer}")
    return answer