# client/server.py
from fastapi import FastAPI, Query
from celery.result import AsyncResult

# Import the *same* Celery app instance (uses the configured backend)
from worker.celery_app import app as celery_app
from worker.customtasks import process_query

app = FastAPI()


@app.get("/")
def root():
    return {"status": "Server is up and running!"}


@app.post("/chat")
def chat(query: str = Query(..., description="User query")):
    """Queue the RAG task and return the job id."""
    task = process_query.delay(query)
    return {"status": "queued", "job_id": task.id}


@app.get("/job-status")
def job_status(job_id: str = Query(..., description="Celery job id")):
    """Poll the result of a queued job."""
    result: AsyncResult = celery_app.AsyncResult(job_id)

    if result.ready():
        if result.successful():
            return {"status": "completed", "result": result.get()}
        else:
            return {"status": "failed", "error": str(result.result)}
    else:
        return {"status": "processing"}