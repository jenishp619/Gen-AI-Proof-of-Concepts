
import os
from pathlib import Path
import sys
from typing import Any, List, Dict
from mcp import stdio_server
from mcp.server.fastmcp import FastMCP, Context

# ONE-LINER VERSION — super common in production MCP servers
if not os.getenv("MCP_DEBUG_STDOUT"):          # set to 1 only when you really need prints
    sys.stdout.write = lambda s: None          # ← nuclear silent mode
    sys.stdout.flush = lambda: None

# Create the MCP server
mcp = FastMCP("filesystem")

# 2) Configure a base directory for safety
#    Change this to the folder you want to expose to the LLM.
BASE_DIR = Path(r"C:\Users\Jenish.Patel\PycharmProjects").resolve()

def _resolve_path(relative_path: str) -> Path:
    """
    Resolve a user-provided relative path under BASE_DIR, and prevent
    escaping above the base directory (simple security guard).
    """
    target = (BASE_DIR / relative_path).resolve()

    # Do not allow paths outside BASE_DIR
    if BASE_DIR != target and BASE_DIR not in target.parents:
        raise ValueError("Requested path is outside the allowed base directory.")

    return target



# Sampling section (“Servers can request LLM completions from clients using sampling.createMessage.”)


@mcp.tool()
def list_directory(relative_path: str = ".") -> List[Dict[str,Any]]:
    """
    List files and folder in BASE_DIR /relative path.

    Args:
        relative_path: Path relative to the configured base directoy. Default "." = the base directory itself.
    """
    path = _resolve_path(relative_path)


    if not path.exists():
        raise FileNotFoundError(f"Path does not exist:{path}")
    
    entries: List[Dict[str,Any]] = []
    for child in path.iterdir():
        entries.append(
            {
                "name":child.name,
                "type":"dictionary" if child.is_dir() else "file",
                "absolute_path": str(child),
            }
        )
    return entries

@mcp.tool()
def read_file(relative_path: str, max_bytes: int=4000) -> Dict[str,Any]:
    """
    Read the contents of a text file under BASE_DIR.

    Args:
        relative_path: File path relative to BASE_DIR.
        max_bytes: Maximum number of bytes to read(for safety)    
    """

    path = _resolve_path(relative_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if not path.is_file():
        raise ValueError(f"Not a file: {path}")
    
    data = path.read_bytes()[:max_bytes]
    try:
        text = data.decode("utf-8",errors="replace")
    except Exception:
        text = ""

    return {
        "relative_path":relative_path,
        "absolute_path": str(path),
        "size_bytes": path.stat().st_size,
        "content_preview": text,
    }

@mcp.tool()
def search_files(pattern: str = "*.py", relative_path: str=".") -> List[Dict [str, Any]]:
    """
    Search for files matching a pattern under BASE_DIR / relative_path
    Pattern examples:
      *.py = all Python files
      *log* = files containing 'log'
      *.md = markdown file
      *.txt = doc files
    """
    root = _resolve_path(relative_path)
    if not root.exists() or not root.is_dir():
        raise ValueError("Invalud directory path.")
    results = []

    for p in root.rglob(pattern):
        if p.is_file():
            results.append({
                "name": p.name,
                "absolute_path": str(p),
                "relative_path":str(p.relative_to(BASE_DIR))
            })
    return results

@mcp.tool()
def grep_text(query: str,relative_path: str=".", extensions: List[str] = [".txt",".md",".py"]) -> List[Dict[str,Any]]:
    """
    Search for a text query inside files.    
    """
    root = _resolve_path(relative_path)
    if not root.exists():
        raise ValueError("Invalid directory path.")
    matches = []

    for p in root.rglob("*"):
        if p.is_file() and any(p.name.endswith(ext) for ext in extensions):
            try:
                for i,line in enumerate(p.read_text(errors="ignore").splitlines(), start=1):
                    if query.lower() in line.lower():
                        matches.append({
                            "file":str(p.relative_to(BASE_DIR)),
                            "line_number":i,
                            "snippet": line.strip()
                        })
            except Exception:
                continue
                    
    return matches


@mcp.tool()
def file_metadata(relative_path: str) -> Dict[str,Any]:
    
    """
    Return the metadata about a file
    """
    path = _resolve_path(relative_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found:{path}")
    if not path.is_file():
        raise ValueError(f"Path is not a file:{path}")
    stats = path.stat()

    return {
        "relative_path": relative_path,
        "absolute_path": str(path),
        "size_bytes": stats.st_size,
        "created": stats.st_birthtime,
        "modified": stats.st_mtime,
        "is_hidden": path.name.startswith("."),
        "extension": path.suffix
    }

@mcp.tool()
def write_file(
    relative_path: str,\
    content: str,
    allow_overwrite: bool = False
) -> Dict[str,Any]:
    """
    Safely write text content to a file under BASE_DIR.
    """
    path = _resolve_path(relative_path)
    if path.exists() and not allow_overwrite:
        raise ValueError("File already exists. Set allow_overwrite=True to overwrite.")
    # Ensure parent directories exist 
    path.parent.mkdir(parents=True,exist_ok=True)

    path.write_text(content,encoding="utf-8")

    return {
        "status":"success",
        "relative_path": relative_path,
        "absolute_path": str(path)
    }
                        
@mcp.tool()
def delete_file(relative_path: str, confirm: bool = False) -> Dict[str, Any]:
    """
    Safely delete a file. Requires confirm=True.
    """
    path = _resolve_path(relative_path)

    if not confirm:
        raise ValueError("Deletion requires confirm=True.")

    if not path.exists():
        raise FileNotFoundError(f"Path does not exist: {path}")
    if not path.is_file():
        raise ValueError("Can only delete files, not directories.")

    path.unlink()

    return {
        "status": "deleted",
        "relative_path": relative_path
    }
def _tree(path: Path, depth: int = 3):
    """
    Internal recursive function to build a folder tree structure.
    """
    if depth == 0:
        return {"name": path.name, "type": "directory", "children": []}

    children = []
    for item in path.iterdir():
        if item.is_dir():
            children.append(_tree(item, depth - 1))
        else:
            children.append({
                "name": item.name,
                "type": "file",
                "extension": item.suffix
            })

    return {"name": path.name, "type": "directory", "children": children}


@mcp.tool()
def folder_tree(relative_path: str = ".", depth: int = 3) -> Dict[str, Any]:
    """
    Return a recursive folder tree.
    depth: limits recursion to protect performance
    """
    path = _resolve_path(relative_path)
    if not path.exists() or not path.is_dir():
        raise ValueError("Invalid directory path.")

    return _tree(path, depth)

@mcp.tool()
def disk_usage(relative_path: str = ".") -> Dict[str, Any]:
    """
    Return total size of directory in bytes.
    """
    path = _resolve_path(relative_path)
    if not path.exists() or not path.is_dir():
        raise ValueError("Invalid directory path.")

    total = 0
    for p in path.rglob("*"):
        if p.is_file():
            total += p.stat().st_size

    return {
        "relative_path": relative_path,
        "total_size_bytes": total
    }


# Simple run: SDK handles initialization and stdio transport
if __name__ == "__main__":
    print("hello there ! mcp checking ")
    print("🚀 Filesystem MCP Server starting... (9 tools ready)", file=sys.stderr)
    mcp.run()