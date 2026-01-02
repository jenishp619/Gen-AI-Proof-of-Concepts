# MCP Filesystem Server (POC)

Local File Operations via Model Context Protocol

This Proof of Concept (POC) implements a specialized Model Context Protocol (MCP) server that enables Large Language Models to interact with the local filesystem. By decoupling file operations from the model's core logic, this server provides a secure, auditable, and standardized interface for agentic file manipulation.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install dependencies.

```bash
pip install mcp
```

## 🛠️ Core Capabilities

This server exposes a suite of tools designed for project exploration, file management, and data retrieval:

| Tool           | Purpose                                       |
| -------------- | --------------------------------------------- |
| list_directory | Base directory listing for navigation         |
| read_file      | UTF-8 encoded file content retrieval          |
| search_files   | Pattern-based file discovery                  |
| grep_text      | Deep-content string matching                  |
| file_metadata  | Structured file info (size, timestamps)       |
| write_file     | Atomic file writing/creation                  |
| delete_file    | Controlled file removal                       |
| folder_tree    | Recursive visualization of project structure  |
| disk_usage     | Storage footprint analysis for specific paths |

## 🧪 Testing & Debugging

The MCP Inspector is used to validate tool schemas and server responses before deployment to an agent client.

### 1. Launching via Development Mode

The most efficient way to debug the fs_server.py is using the mcp dev command:

```bash
mcp dev .\fs_server.py
```

### 2. Manual Configuration (Universal Path)

If you are running the inspector via npx or configuring it for a specific environment (like a GPT client), use the following execution arguments:

use your (absolute path)

```bash
run --with mcp mcp run "C:\POC\mcp-dev\mcp_fs_server\fs_server.py"
```

### 3. Validation Workflow

- **Open the Inspector:** Navigate to the URL provided in your terminal (usually localhost:6274).
- **Setup Path:** Ensure the "Arguments" field in the UI matches your local project directory.
- **Execute:** Select the list_directory tool and click Run.
- **Inspect JSON:** Check the output logs to ensure the server is returning valid JSON tool responses.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
