# Model Context Protocol (MCP) - Interview Ready

## What is MCP?

Standardized protocol that allows LLMs to safely interact with external systems (databases, APIs, files) through **Client-Server architecture**.

**Key Benefits:**

- Decouples AI logic from system operations
- Secure sandboxed execution
- Unified interface for all integrations
- Scalable across multiple servers

---

## Architecture

```
Claude/Gemini → MCP Server → PostgreSQL/APIs/Filesystem
```

---

## 3 Core Components

**Tools** - Executable functions (CRUD, API calls, file ops)  
**Resources** - Data URLs (efficient data access)  
**Prompts** - Pre-configured instructions

---

## Your MCP Implementations

### 1. Filesystem Server (`mcp_fs_server/`)

- list_directory, read_file, write_file, delete_file, search_files
- grep_text, file_metadata, folder_tree, disk_usage
- **Security**: All ops confined to BASE_DIR (prevents directory traversal)

### 2. Document Server (`MCP-anthropic/cli_project/`)

- Tools: read_doc, edit_document
- Resources: docs://documents, docs://documents/{id}
- Prompts: format_document (AI-guided formatting)

### 3. Notification Server (`MCP-anthropic/notifications/`)

- send_notification (Slack/Email/SMS)
- get_notification_history

---

## Production Use Cases

### Case 1: PostgreSQL Integration

```python
# Claude reads/writes to DB through MCP server
Claude: "Create user john@example.com"
  → create_user() → INSERT to PostgreSQL

Claude: "List all admin users"
  → list_users(role="admin") → Query results
```

**Tools Available:**

- create_user, update_user, delete_user, get_user
- list_users (with filtering & pagination)
- search_users (full-text search)
- get_user_stats, execute_custom_query

**Resources:**

- postgres://users/all
- postgres://users/{user_id}
- postgres://stats

### Case 2: Multi-Server Setup

```python
# Single Claude agent + 3 MCP Servers
Claude → Filesystem MCP (read/write files)
      → PostgreSQL MCP (database ops)
      → API MCP (external APIs)

# Claude can do all 3 transparently in conversation
```

### Case 3: Agentic Workflow

```python
Order Processing:
1. Create order in PostgreSQL
2. Check inventory (DB query)
3. Process payment (Payment API)
4. Send confirmation (Email MCP)
5. Log to analytics (Analytics MCP)
```

---

## Deployment

| Option         | Use Case                  |
| -------------- | ------------------------- |
| **Stdio**      | Development (direct pipe) |
| **HTTP/S**     | Production REST API       |
| **Docker**     | Microservices/containers  |
| **Kubernetes** | Enterprise orchestration  |

---

## Why MCP Matters

✓ **Secure** - Operations sandboxed from LLM  
✓ **Standardized** - One protocol for all systems  
✓ **Scalable** - Multiple servers, one agent  
✓ **Auditable** - All tool calls logged  
✓ **Reusable** - Works with Claude, Gemini, OpenAI

---

## Summary

**"MCP is how you safely give LLMs the ability to interact with real systems - databases, APIs, files - without them running arbitrary code. Think of it as a plugin system for AI agents."**

**Key Points:**

- Decouples AI from implementation
- Secure sandboxing
- Scale across multiple servers
- Real-world: payments, databases, notifications
- Enterprise-ready with full auditability
