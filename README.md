# Generative AI & Agentic Systems: Implementation Lab

This repository contains a collection of technical implementations developed during an Agentic AI Intensive. It covers core fundamentals and hands-on functional demos of Agentic AI systems, including Retrieval-Augmented Generation (RAG), Model Context Protocol (MCP), and multi-model orchestration

---

## Purpose

This repository serves as a comprehensive, hands-on reference for
Agentic AI fundamentals and their integration with different LLM
providers. The projects focus on practical, executable systems rather
than theoretical examples, demonstrating how modern AI agents are
designed, orchestrated, and deployed.

It is intended for technical evaluation, learning, and discussion,
particularly in the context of real-world AI application development.

---

## Overview

The projects demonstrate practical applications of AI technologies
using modern frameworks and APIs. Each folder represents a separate,
independent project with its own focus, tooling, and documentation.

All projects are currently runnable and demonstrate working
implementations of the respective concepts.

---

## Repository Structure

Each top-level folder represents a standalone project or concept within
Agentic AI. Projects are self-contained, with their own dependencies,
configuration, and setup instructions.

Most subprojects include their own README files that provide deeper
details on architecture, usage, and implementation decisions.

---

## Prerequisites

- Python 3.9+
- API keys for relevant providers (OpenAI, Anthropic, Gemini, etc.),
  depending on the project
- Docker (required for containerized services such as vector databases
  or background workers)

---

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/jenishp619/Gen-AI-Proof-of-Concepts.git
   cd Gen-AI-Proof-of-Concepts
   ```

## Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd Gen-AI-Proof-of-Concepts
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

**Purpose:** Comprehensive development of MCP (Model Context Protocol) servers and clients for AI model interactions, covering both fundamentals and advanced implementations.  
**Technologies:** Python, MCP library, Anthropic API, Gemini API, OpenAI API, FastAPI, various LLMs.  
**Key Files/Subprojects:**

- **mcp_fs_server/** - File system MCP server with SSE support for file operations.
- **MCP-anthropic/cli_project/** - CLI-based chat application integrating multiple LLMs (Anthropic Claude, Gemini, OpenAI).
- **MCP-anthropic/notifications/** - Notification system using MCP for real-time updates.
- **MCP-anthropic/roots/** - Advanced MCP implementation with video conversion tools and multi-LLM support.
- **MCP-anthropic/sampling/** - Sampling strategies for MCP interactions with Gemini API.

**Description:** A complete hub for MCP implementations, encompassing all Anthropic MCP fundamentals (basic server-client setups, tool integrations) and advanced tasks (multi-modal processing, video handling, sampling techniques). Fully integrated with Gemini API for enhanced AI capabilities, alongside Anthropic and OpenAI models. Includes tools for file operations, chat interfaces, notifications, and custom utilities. Each subproject has detailed READMEs for setup and usage.

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

### 9. Todo App(This is not present and if you would like to create then please use agent present in weather_agent)

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

Contributions & Feature Requests

This repository is not open to external code contributions.

However, discussions and feature requests related to Agentic AI
concepts, integrations, or extensions are welcome and may guide future
development.

## Usage Notice

This repository is shared publicly for learning, review, and technical
evaluation purposes. You are welcome to explore the code and run it
locally for personal understanding.

Please do not reuse, redistribute, or deploy this code in production
systems without explicit permission from the author.

## License

Copyright © 2026 Jenish Patel  
All rights reserved.
