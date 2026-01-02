# Agentic AI Course Projects

This repository contains a collection of projects and implementations developed during an Agentic AI course. It covers various topics in AI agent development, including Retrieval-Augmented Generation (RAG), Model Context Protocol (MCP), voice agents, memory systems, prompting techniques, and more.

## Overview

The projects demonstrate practical applications of AI technologies using modern frameworks and APIs. Each folder represents a separate project with its own focus and technologies.

## Prerequisites

- Python 3.9+
- Various API keys (OpenAI, Anthropic, etc.) depending on the project
- Docker (for containerized services)

## Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd Agentic-AI-course
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables for API keys in `.env` files as needed for each project.

## Projects

### 1. Hugging Face Demo

**Purpose:** Demonstrates multimodal AI using Hugging Face Transformers for image-text-to-text tasks.  
**Technologies:** Hugging Face Transformers, Python.  
**Key Files:** `server.py` - Loads Google's Gemma model to analyze images and answer questions.  
**Description:** A demo script that processes images and text queries to generate responses, showcasing multimodal capabilities.

### 2. LangGraph Learn

**Purpose:** Learning materials for building conversational AI agents using LangGraph.  
**Technologies:** LangChain, LangGraph, OpenAI, Python.  
**Key Files:**

- `chat.py` - Basic LangGraph workflow with chatbot nodes.
- `chat_2.py`, `chat_checkpoint.py` - Additional variations.
- `docker-compose.yml` - Container setup.  
  **Description:** Examples of stateful, graph-based workflows for AI conversations, integrating with OpenAI models.

### 3. MCP Dev

**Purpose:** Development of MCP (Model Context Protocol) servers and clients for AI model interactions.  
**Technologies:** Python, MCP library, Anthropic API, FastAPI, various LLMs.  
**Key Files:** Multiple subprojects including file system servers, CLI chat apps, and notification systems.  
**Description:** A hub for MCP implementations, featuring integrations with Anthropic, OpenAI, Gemini, and tools for file operations, chat, and more. Includes detailed READMEs in subfolders.

### 4. Memory Agent

**Purpose:** Implementation of a persistent memory system for AI applications.  
**Technologies:** Mem0, Qdrant, Neo4j, OpenAI, Python.  
**Key Files:**

- `mem.py` - Initializes Mem0 client with vector and graph databases.
- `mem_graph.py`, `memnew.py` - Additional memory operations.
- `docker-compose.yml` - Service orchestration.  
  **Description:** Hybrid memory system using vector embeddings and graph structures for context-aware AI interactions.

### 5. Ollama FastAPI

**Purpose:** REST API server for local AI model interactions using Ollama.  
**Technologies:** FastAPI, Ollama, Python.  
**Key Files:** `server.py` - Defines API endpoints for chat with local models.  
**Description:** Lightweight server exposing endpoints to interact with Ollama-hosted models like Gemma.

### 6. Prompt Techniques

**Purpose:** Exploration of various prompting strategies for AI models.  
**Technologies:** OpenAI client (configured for Gemini), Python.  
**Key Files:**

- `main.py` - Example with system prompts.
- `chain-of-thought.py`, `few-shot.py`, `persona.py`, `zero.py` - Different prompting methods.
- `prompt_style.md` - Documentation on styles.  
  **Description:** Collection of examples demonstrating advanced prompting techniques for better AI responses.

### 7. RAG System

**Purpose:** Retrieval-Augmented Generation system for querying PDF documents.  
**Technologies:** LangChain, Qdrant, OpenAI, Python.  
**Key Files:**

- `chat.py` - Performs similarity search and generates answers.
- `index.py` - Document indexing.
- `docker-compose.yml` - Qdrant setup.  
  **Description:** Vector-based retrieval system that embeds documents, retrieves relevant chunks, and generates context-aware responses.

### 8. RAG Queue

**Purpose:** Asynchronous RAG system with task queuing for scalable document processing.  
**Technologies:** FastAPI, Celery, Python.  
**Key Files:**

- `main.py`, `server.py` - API server.
- `worker/` - Celery tasks for background processing.
- `docker-compose.yaml` - Service orchestration.  
  **Description:** Queued system allowing asynchronous indexing and querying of documents using Celery workers.

### 9. Todo App

**Purpose:** Simple web-based todo list application.  
**Technologies:** HTML, CSS, JavaScript.  
**Key Files:**

- `index.html` - Main UI structure.
- `style.css` - Styling.
- `script.js` - Interactivity for adding/removing tasks.  
  **Description:** Client-side todo app with basic task management functionality.

### 10. Voice Agent

**Purpose:** Voice-based conversational AI agent with speech recognition and synthesis.  
**Technologies:** SpeechRecognition, OpenAI, Python.  
**Key Files:**

- `main.py` - Main agent script with STT and TTS.
- `agent.py` - Additional agent logic.  
  **Description:** Agent that listens to user speech, processes queries with LLM, and responds via voice.

### 11. Weather Agent

**Purpose:** AI agent for weather queries with API integration.  
**Technologies:** OpenAI, Requests, Python.  
**Key Files:**

- `main.py` - Weather fetching and chat interface.
- `agent.py` - Agent implementation.  
  **Description:** Simple agent that retrieves weather data from external APIs and provides responses via chat.

## Contributing

Feel free to explore, modify, and extend these projects. Each folder is self-contained with its own dependencies and setup.

## License

Copyrights reserved by Jenish Patel</content>
