# ProcExecMCP

**Stateless command execution and process management MCP server for Claude**

ProcExecMCP enables Claude (acting in an architectural role on Windows) to search code content, execute commands, monitor processes, and terminate processes. The server exposes 4 MCP tools using FastMCP with Python 3.11+, psutil for cross-platform process management, and system ripgrep for file content search.

## Features

- 🔍 **search_file_contents**: Search for patterns in file contents using ripgrep
- ⚡ **execute_command**: Execute commands safely with timeout and output limits  
- 📊 **list_processes**: List running processes with filtering and sorting
- 🛑 **kill_process**: Terminate processes by PID

## Security

- ✅ No shell injection (no `shell=True`)
- ✅ Mandatory timeouts on all operations
- ✅ Resource limits prevent memory exhaustion
- ✅ Path validation prevents traversal attacks
- ✅ Sanitized error messages

## Prerequisites

- Python 3.11+
- uv package manager
- ripgrep binary
- Claude for Windows

## Installation

See [Quickstart Guide](./specs/001-procexec-mcp-server/quickstart.md) for detailed instructions.

## Configuration

### Environment Variables

- **PROCEXEC_RIPGREP_PATH**: Optional. Full path to ripgrep binary. Use this if ripgrep is not in your system PATH or when Claude Desktop has limited PATH access on Windows.

  Example configuration in Claude Desktop:
  ```json
  {
    "mcpServers": {
      "procexec": {
        "command": "uv",
        "args": ["run", "procexec"],
        "env": {
          "PROCEXEC_RIPGREP_PATH": "C:\\tools\\ripgrep\\rg.exe"
        }
      }
    }
  }
  ```

- **PROCEXEC_TIMEOUT**: Command execution timeout in milliseconds (default: 30000)
- **PROCEXEC_MAX_OUTPUT**: Maximum output size in bytes (default: 10485760)
- **PROCEXEC_BLOCKED_PATHS**: Comma-separated list of paths to block access to

## License

MIT
