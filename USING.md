# Using ProcExecMCP

## For Developers

This guide is for developers who want to fork, modify, or contribute to ProcExecMCP. For end-user installation and usage, see [README.md](./README.md).

## Prerequisites

- Python 3.11 or higher
- uv package manager
- ripgrep binary
- Git with GPG signing configured (for contributions)

## Development Setup

### 1. Clone Repository

```bash
git clone https://github.com/positronikal/procexec-mcp.git
cd procexec-mcp
```

### 2. Install Dependencies

```bash
# Install all dependencies including development tools
uv sync

# Verify installation
uv run python -c "import procexec; print('ProcExecMCP installed')"
```

### 3. Install ripgrep

Ensure ripgrep is available:

```bash
# Verify ripgrep
rg --version

# Install if needed
# Windows: winget install BurntSushi.ripgrep.MSVC
# macOS: brew install ripgrep
# Linux: sudo apt install ripgrep
```

## Project Structure

```
ProcExecMCP/
├── src/procexec/          # Main package
│   ├── __init__.py        # Package initialization
│   ├── __main__.py        # Entry point
│   ├── server.py          # FastMCP server setup
│   ├── tools/             # MCP tool implementations
│   │   ├── search.py      # search_file_contents tool
│   │   ├── execute.py     # execute_command tool
│   │   ├── processes.py   # list_processes, kill_process tools
│   │   └── schemas.py     # Pydantic models for validation
│   └── utils/             # Shared utilities
│       ├── validation.py  # Path validation, error sanitization
│       └── platform.py    # Cross-platform compatibility
├── tests/                 # Test suite
│   ├── unit/              # Unit tests (mocked dependencies)
│   ├── integration/       # Integration tests (real execution)
│   └── security/          # Security validation tests
├── specs/                 # Specification documents
├── docs/                  # API documentation (Doxygen generated)
└── etc/                   # Archived documentation (gitignored)
```

## Running Tests

### All Tests

```bash
uv run pytest
```

### Test Categories

```bash
# Unit tests only (fast, mocked)
uv run pytest tests/unit/ -v

# Integration tests (real execution)
uv run pytest tests/integration/ -v

# Security tests (attack validation)
uv run pytest tests/security/ -v
```

### Coverage

```bash
# Generate coverage report
uv run pytest --cov=src/procexec --cov-report=html

# View HTML report
open htmlcov/index.html  # macOS/Linux
start htmlcov/index.html # Windows
```

### Test Requirements

- All contributions must maintain >80% code coverage
- Security tests must pass 100%
- Cross-platform tests should pass on Windows and Unix

## Running the Server

### Development Mode

```bash
# Run with stdio transport (for MCP Inspector)
uv run procexec

# Run as module
uv run python -m procexec
```

### Testing with MCP Inspector

```bash
# Terminal 1: Start server
uv run procexec

# Terminal 2: Start inspector
npx @modelcontextprotocol/inspector

# Connect to: http://localhost:8000/mcp
```

### Integration with Claude Desktop

See [README.md](./README.md) for Claude Desktop configuration.

## Available Tools

### 1. search_file_contents

Search for patterns in files using ripgrep.

**Capabilities:**
- Regex pattern matching
- File type filtering
- Path exclusion patterns
- Context lines (before/after match)
- Result limiting

**Security:**
- Path traversal prevention
- Blocked path enforcement
- Regex length limits (prevents ReDoS)

### 2. execute_command

Execute commands safely with timeout and output limits.

**Capabilities:**
- Safe subprocess execution (no shell injection)
- Configurable timeouts
- Output size limits
- Working directory specification
- Cross-platform support

**Security:**
- **Never uses shell=True**
- Command argument parsing with shlex
- Timeout enforcement
- Output truncation
- Error message sanitization

### 3. list_processes

List running processes with filtering and sorting.

**Capabilities:**
- Process enumeration
- Name-based filtering
- Sorting (CPU, memory, PID, name)
- Result limiting

**Security:**
- Graceful handling of permission errors
- No privileged process information leakage

### 4. kill_process

Terminate processes by PID.

**Capabilities:**
- Graceful termination (SIGTERM/WM_CLOSE)
- Forced termination (SIGKILL/TerminateProcess)
- Configurable timeout
- Cross-platform support

**Security:**
- Disabled by default (PROCEXEC_ENABLE_KILL required)
- PID validation
- Permission error handling
- OS-level protection for system processes

## Architecture

### Design Principles

1. **Unix Philosophy**: Each tool does one thing well
2. **Stateless Design**: No session persistence
3. **Security First**: No compromises on safety
4. **Cross-Platform**: Windows and Unix support
5. **Minimal Dependencies**: Only essential libraries

### Key Components

**Server (server.py)**:
- FastMCP integration
- Configuration management
- Environment variable loading

**Tools (tools/*.py)**:
- Individual tool implementations
- Helper functions (single responsibility)
- MCP tool decorators

**Schemas (tools/schemas.py)**:
- Pydantic input validation
- Output structure definitions
- Error categories

**Utilities (utils/*.py)**:
- Path validation
- Error sanitization
- Platform detection

### Security Architecture

See [SECURITY_ARCHITECTURE.md](./SECURITY_ARCHITECTURE.md) for comprehensive security documentation.

## Adding New Tools

### 1. Define Schemas

```python
# In src/procexec/tools/schemas.py

class NewToolInput(BaseModel):
    param: str = Field(description="Parameter description")
    
class NewToolOutput(BaseModel):
    result: str = Field(description="Result description")
```

### 2. Implement Tool

```python
# In src/procexec/tools/newtool.py

from ..server import mcp
from .schemas import NewToolInput, NewToolOutput

@mcp.tool()
async def new_tool(param: str) -> NewToolOutput:
    """Tool description for Claude."""
    # Validate input
    input_data = NewToolInput(param=param)
    
    # Perform operation
    result = do_something(input_data.param)
    
    # Return structured output
    return NewToolOutput(result=result)
```

### 3. Add Tests

```python
# In tests/integration/test_newtool_integration.py

import pytest
from src.procexec.tools.newtool import new_tool

@pytest.mark.asyncio
async def test_new_tool():
    result = await new_tool("test")
    assert result.result == "expected"
```

### 4. Export Tool

```python
# In src/procexec/tools/__init__.py

from .newtool import new_tool
__all__ = ["search_file_contents", "execute_command", "list_processes", "kill_process", "new_tool"]
```

## Advanced Configuration

### Custom Blocked Paths

```json
"env": {
  "PROCEXEC_BLOCKED_PATHS": "/etc/shadow,/etc/passwd,C:\\Windows\\System32\\config"
}
```

### Custom ripgrep Path

```json
"env": {
  "PROCEXEC_RIPGREP_PATH": "/opt/homebrew/bin/rg"
}
```

### Increased Timeouts

```json
"env": {
  "PROCEXEC_TIMEOUT": "60000",
  "PROCEXEC_MAX_OUTPUT": "52428800"
}
```

## Debugging

### Enable Python Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Claude Desktop Logs

- **Windows**: `%APPDATA%\Claude\logs\`
- **macOS**: `~/Library/Logs/Claude/`
- **Linux**: `~/.config/Claude/logs/`

### Test Individual Tools

```python
import asyncio
from src.procexec.tools.search import search_file_contents

async def test():
    result = await search_file_contents(
        pattern="TODO",
        path="./src"
    )
    print(result)

asyncio.run(test())
```

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for contribution guidelines.

### Development Workflow

1. Fork repository
2. Create feature branch
3. Implement changes with tests
4. Ensure all tests pass
5. Maintain >80% coverage
6. Submit pull request

### Code Standards

- Follow [Positronikal Coding Standards](https://github.com/positronikal/coding-standards)
- Use procedural programming patterns
- Write comprehensive tests
- Document all public functions
- Sanitize all error messages

## Building Documentation

### Generate Doxygen Docs

```bash
# Generate API documentation
doxygen Doxyfile

# View generated docs
open docs/html/index.html
```

Documentation will be generated in `docs/` directory.

## Deployment

### Binary Distribution (PyInstaller)

```bash
# Install PyInstaller
uv add pyinstaller --dev

# Build binary
uv run pyinstaller --onefile src/procexec/__main__.py

# Binary location
dist/procexec.exe  # Windows
dist/procexec      # Unix
```

### Package Distribution

```bash
# Build package
uv build

# Install from package
pip install dist/procexec-1.0.0-py3-none-any.whl
```

## Troubleshooting

See [BUGS.md](./BUGS.md) for common issues and solutions.

## Additional Resources

- **API Documentation**: `docs/` (Doxygen generated)
- **Specification**: `specs/001-procexec-mcp-server/`
- **Security**: [SECURITY_ARCHITECTURE.md](./SECURITY_ARCHITECTURE.md)
- **Positronikal Standards**: https://positronikal.github.io/
