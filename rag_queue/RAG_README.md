# RAG (Retrieval-Augmented Generation) Implementation

## Overview

Production-ready RAG system that grounds LLM responses in document context, eliminating hallucinations and providing source attribution.

## System Architecture

### Simple RAG (`/rag`)

```
PDF Document → Embeddings Index → Vector DB (Qdrant)
                                        ↓
User Query → Similarity Search → Context Retrieval → LLM Response → Answer with Page Numbers
```

### RAG with Task Queue (`/rag_queue`)

```
Client Request → FastAPI → Redis Queue → Worker Process → LLM → Result Backend
     ↓            ↓            ↓              ↓             ↓          ↓
User Query   Returns job_id  Persists      Retrieves    Streams    Stores in
             immediately      tasks        context      response    Redis
```

---

## Core Pipeline

### Phase 1: Indexing (One-Time Setup)

```python
1. Load PDF pages → PyPDFLoader
2. Split into chunks → RecursiveCharacterTextSplitter (1000 chars, 400 char overlap)
3. Generate embeddings → OpenAI text-embedding-3-large
4. Store in vector DB → Qdrant (localhost:6333)
```

**Why overlap?** Preserves context at chunk boundaries for better semantic understanding.

### Phase 2: Retrieval (Per Query)

```python
1. Embed user query (same model as indexing)
2. Similarity search in Qdrant → Top-k chunks (k=4)
3. Build context from metadata (page numbers, content)
4. Send context + query to LLM with system prompt
```

### Phase 3: Generation

- **System Prompt**: Constrains LLM to answer only from provided context
- **Model**: GPT-4 (production) / GPT-3.5-turbo (cost-efficient)
- **Result**: Answer with source page attribution

---

## Key Technology Stack

| Component       | Purpose                             | Technology                    |
| --------------- | ----------------------------------- | ----------------------------- |
| Vector DB       | Store embeddings, similarity search | Qdrant                        |
| Embedding Model | Text → Vector conversion            | OpenAI text-embedding-3-large |
| LLM             | Generate answers                    | GPT-4 / GPT-3.5-turbo         |
| Task Queue      | Async processing                    | Celery                        |
| Message Broker  | Task persistence                    | Redis/Valkey                  |
| Web Framework   | API endpoints                       | FastAPI                       |

---

## Critical Design Decisions

### 1. **Chunking Strategy**

- **Size**: 1000 characters (balance between context and complexity)
- **Overlap**: 400 chars (prevents context loss at boundaries)
- **Benefit**: Semantic coherence without token inflation

### 2. **Vector Database**

- **Choice**: Qdrant (low-latency, in-memory)
- **Collection**: Named collections for multi-document scenarios
- **Search Type**: Cosine similarity for semantic matching

### 3. **Async Architecture (rag_queue)**

- **Problem Solved**: Long-running queries don't block API
- **Concurrency**: Single worker (easily scalable)
- **Persistence**: Tasks survive service restarts
- **Result TTL**: 1 hour (balances storage vs. query window)

### 4. **Context Grounding**

- System prompt constraints LLM to context only
- Metadata includes page numbers for user verification
- Prevents hallucinations through explicit scope limitation

---

## API Endpoints

### Simple RAG

```bash
POST /chat?query="Your question"
# Returns: Immediate answer with page attribution
```

### RAG Queue (Async)

```bash
POST /chat?query="Your question"
# Returns: {"status": "queued", "job_id": "abc-123"}

GET /job-status?job_id=abc-123
# Returns:
#   - {"status": "processing"}
#   - {"status": "completed", "result": "..."}
#   - {"status": "failed", "error": "..."}
```

---

## Performance Characteristics

| Metric            | Value         | Notes                      |
| ----------------- | ------------- | -------------------------- |
| Embedding Time    | ~100ms        | One-time on indexing       |
| Similarity Search | ~50ms         | Vector DB lookup           |
| Context Building  | ~20ms         | String concatenation       |
| LLM Inference     | ~2-5s         | Dominant cost factor       |
| **Total Latency** | **2.2-5.2s**  | Simple RAG direct response |
| **Response Time** | **Immediate** | RAG Queue returns job_id   |

---

## Advantages Over Base LLM

| Aspect             | Base LLM                | RAG System                    |
| ------------------ | ----------------------- | ----------------------------- |
| Accuracy           | Knowledgebase cutoff    | Current/custom documents      |
| Hallucinations     | High (confabulates)     | Minimal (grounded in context) |
| Source Attribution | None                    | Page numbers included         |
| Context Control    | Fixed                   | Custom document selection     |
| Cost               | Higher (longer context) | Lower (minimal tokens)        |
| Scalability        | Single request          | Multiple concurrent queries   |

---

## Docker Infrastructure

```yaml
valkey: Redis compatible message broker
- Task queue storage
- Result backend (1-hour TTL)
- High-performance, single-threaded
```

---

## Production Considerations

### Implemented ✓

- Context length limiting
- Temperature tuning (0.3 - more deterministic)
- JSON serialization (no Python objects)
- Windows-compatible worker pool (solo mode)
- Error handling with job status tracking

### Ready to Add

- Authentication (API keys)
- Rate limiting per user
- Multiple worker scaling
- Database persistence (backup results beyond 1 hour)
- Monitoring & logging (failures, latency)
- A/B testing (model versions)

---

## Use Cases

| Scenario                 | Recommendation            |
| ------------------------ | ------------------------- |
| Document Q&A chatbots    | RAG Queue (multi-user)    |
| Internal knowledge bases | RAG Queue (scalable)      |
| Real-time applications   | Simple RAG (low latency)  |
| High-concurrency APIs    | RAG Queue + multi-workers |

---

## Summary for POC

**What**: LLM grounding system using document retrieval  
**Why**: Eliminates hallucinations, ensures accuracy, provides sources  
**How**: Embeddings → Vector search → Context injection → LLM  
**Scale**: Async queue handles multiple concurrent users  
**Tech**: Qdrant + Redis + OpenAI + FastAPI  
**Ready**: Production architecture with error handling and monitoring hooks
