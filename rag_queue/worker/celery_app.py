# worker/celery_app.py
from celery import Celery

# -------------------------------------------------
# 1. Create the Celery application
# -------------------------------------------------
app = Celery("rag_queue")

# -------------------------------------------------
# 2. Valkey (Redis) broker + result backend
# -------------------------------------------------
app.conf.broker_url = "redis://localhost:6379/0"
app.conf.result_backend = "redis://localhost:6379/0"

# -------------------------------------------------
# 3. General settings
# -------------------------------------------------
app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    result_expires=3600,                # clean old results after 1 h
)

# -------------------------------------------------
# 4. Windows-friendly worker pool
# -------------------------------------------------
app.conf.worker_pool = "solo"           # no fork()
app.conf.worker_concurrency = 1
app.conf.worker_prefetch_multiplier = 1

# -------------------------------------------------
# 5. Manual task registration (no autodiscover)
# -------------------------------------------------
# The import is placed **after** the app is fully built
from worker.customtasks import process_query  # noqa: E402