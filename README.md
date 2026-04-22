# ProcExecMCP

**Stateless command execution and process management MCP server for Claude**

ProcExecMCP enables Claude (acting in an architectural role) to search code content, execute commands, monitor processes, and terminate processes. The server exposes 4 MCP tools using FastMCP with Python 3.11+, psutil for cross-platform process management, and system ripgrep for file content search.

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

For comprehensive security documentation, see [SECURITY_ARCHITECTURE.md](./SECURITY_ARCHITECTURE.md).

## Prerequisites

- **Python 3.11+** 
- **uv** package manager ([installation guide](https://docs.astral.sh/uv/))
- **ripgrep (rg)** binary ([installation guide](https://github.com/BurntSushi/ripgrep#installation))
- **Claude Desktop** or **Claude for Windows**

## Quick Start

### 1. Install Dependencies

```bash
# Clone repository
git clone https://github.com/Positronikal/ProcExecMCP.git ProcExecMCP
cd ProcExecMCP

# Install with uv
uv sync
```

### 2. Verify ripgrep

```bash
# Check if ripgrep is installed
rg --version
```

If not installed:
- **Windows**: `winget install BurntSushi.ripgrep.MSVC`
- **macOS**: `brew install ripgrep`
- **Linux**: `sudo apt install ripgrep`

### 3. Configure Claude Desktop

Edit your Claude Desktop configuration file:
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

Add ProcExecMCP to `mcpServers`:

```json
{
  "mcpServers": {
    "procexec": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/ProcExecMCP",
        "run",
        "procexec"
      ],
      "env": {
        "PROCEXEC_TIMEOUT": "30000",
        "PROCEXEC_MAX_OUTPUT": "10485760",
        "PROCEXEC_ENABLE_KILL": "true",
        "PROCEXEC_RIPGREP_PATH": "/path/to/rg"
      }
    }
  }
}
```

**Windows Example**:
```json
{
  "mcpServers": {
    "procexec": {
      "command": "C:\\Users\\YourName\\.local\\bin\\uv.exe",
      "args": [
        "--directory",
        "D:\\dev\\ProcExecMCP",
        "run",
        "procexec"
      ],
      "env": {
        "PROCEXEC_RIPGREP_PATH": "C:\\Program Files\\ripgrep\\rg.exe"
      }
    }
  }
}
```

### 4. Restart Claude Desktop

Close and reopen Claude Desktop to load the new MCP server.

### 5. Verify Installation

In Claude, try:
```
What MCP tools do you have available?
```

You should see all 4 ProcExecMCP tools listed.

## Configuration

### Environment Variables

- **PROCEXEC_TIMEOUT**: Command timeout in milliseconds (default: 30000, range: 1000-300000)
- **PROCEXEC_MAX_OUTPUT**: Maximum output size in bytes (default: 10485760 = 10MB)
- **PROCEXEC_BLOCKED_PATHS**: Comma-separated list of paths to block access
- **PROCEXEC_ENABLE_KILL**: Enable process termination tool (default: "true")
- **PROCEXEC_RIPGREP_PATH**: Full path to ripgrep binary (use if not in PATH)

### Security Considerations

1. **Blocked Paths**: Configure `PROCEXEC_BLOCKED_PATHS` to protect sensitive directories
2. **Process Termination**: Disable with `PROCEXEC_ENABLE_KILL="false"` if not needed
3. **Timeouts**: Set appropriate limits to prevent runaway commands
4. **Privileges**: Avoid running Claude Desktop with elevated privileges unless necessary

## Usage Examples

### Search for Code Patterns

```
Search for all TODO comments in my Python project at /path/to/project
```

### Execute Analysis Tools

```
Run 'pylint src/' in my project directory and show the results
```

### Monitor Processes

```
List all Python processes sorted by memory usage
```

### Terminate Stuck Processes

```
Terminate process 1234 gracefully
```

## Development

For development setup, running tests, modifying the server, and building documentation, see [USING.md](./USING.md).

## Documentation

- **Quick Start**: See above
- **Detailed Usage**: [USING.md](./USING.md)
- **Security Architecture**: [SECURITY_ARCHITECTURE.md](./SECURITY_ARCHITECTURE.md)
- **API Documentation**: `docs/` directory (Doxygen generated)
- **Troubleshooting**: [BUGS.md](./BUGS.md)
- **Contributing**: [CONTRIBUTING.md](./CONTRIBUTING.md)

## Troubleshooting

### ripgrep not found

Ensure ripgrep is installed and in PATH, or set `PROCEXEC_RIPGREP_PATH` environment variable.

### Timeout errors

Increase timeout via `PROCEXEC_TIMEOUT` environment variable (milliseconds).

### Permission denied

Check file/directory permissions or configure `PROCEXEC_BLOCKED_PATHS`.

For more troubleshooting guidance, see [BUGS.md](./BUGS.md).

## License

This project is licensed under the GNU General Public License version 3 or any later version (GPLv3+). See [COPYING.md](./COPYING.md) for the full license text.

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

## Support

- **Issues**: [GitHub Issues](https://github.com/Positronikal/ProcExecMCP/issues)
- **Security**: See [SECURITY.md](./SECURITY.md) for responsible disclosure
- **Documentation**: See `docs/` for API reference
