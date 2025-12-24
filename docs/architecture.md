# Architecture: ProcExecMCP

**Last Updated**: 2025-12-23
**Full Design**: See [plan.md](../specs/001-procexec-mcp-server/plan.md) and [research.md](../specs/001-procexec-mcp-server/research.md)

## Overview

ProcExecMCP is a stateless MCP server built with FastMCP that exposes 4 tools for command execution and process management. The architecture follows procedural programming principles with clear separation of concerns.

## Technology Stack

- **Language**: Python 3.11+
- **MCP Framework**: FastMCP (from mcp Python SDK)
- **Process Management**: psutil (cross-platform)
- **File Search**: System ripgrep binary via subprocess
- **Validation**: Pydantic schemas
- **Packaging**: uv

## Architecture Principles

### 1. Stateless Operation
- Each tool call is completely independent
- No sessions or persistent state between invocations
- Self-contained responses with complete results

### 2. Security-First Design
- No `shell=True` in subprocess calls
- Command parsing with `shlex.split()`
- Path validation prevents traversal attacks
- Timeout enforcement on all operations
- Output size limits prevent resource exhaustion
- Error message sanitization prevents information leakage

### 3. Procedural Programming Style
- Clear module separation: `tools/`, `utils/`
- Functions over classes where possible
- Explicit over implicit behavior
- No framework magic beyond FastMCP decorators

## Module Structure

```
src/procexec/
├── __init__.py          # Package exports
├── __main__.py          # Entry point
├── server.py            # FastMCP server configuration
├── tools/               # MCP tool implementations
│   ├── schemas.py       # Pydantic input/output models
│   ├── search.py        # search_file_contents tool
│   ├── execute.py       # execute_command tool (MVP skipped)
│   └── processes.py     # list/kill_process tools (MVP skipped)
└── utils/               # Cross-cutting utilities
    ├── validation.py    # Path validation, error sanitization
    └── platform.py      # Cross-platform abstractions
```

## Key Design Decisions

### FastMCP Integration
- Use `@mcp.tool()` decorator for automatic tool registration
- Pydantic models for input validation and structured output
- Context injection for logging and progress reporting

### Ripgrep Integration
- System binary invocation via subprocess (no Python library dependency)
- JSON output mode for structured parsing
- Platform-agnostic (works on Windows and Unix)

### Error Handling
- Custom `SanitizedError` exception class
- Automatic message sanitization removes paths, usernames, IPs
- Error categories for programmatic handling by Claude

### Configuration
- Environment variables for runtime configuration
- `ServerConfig` class validates on startup
- Sensible defaults with override capability

## Data Flow

### Tool Invocation Flow
1. Claude sends tool request via MCP protocol
2. FastMCP deserializes and validates input using Pydantic schema
3. Tool function executes with validated parameters
4. Output is serialized as Pydantic model
5. FastMCP returns structured response to Claude

### Search Tool Flow (US1)
1. Validate search pattern and path
2. Build ripgrep arguments (--json, --context, filters)
3. Execute ripgrep via subprocess with timeout
4. Parse JSON output into SearchMatch objects
5. Return SearchFileContentsOutput with matches and metadata

## Cross-Platform Support

- **Platform Detection**: `utils/platform.py` detects Windows vs Unix
- **Command Parsing**: `shlex.split()` with platform-specific `posix` parameter
- **Process Management**: psutil abstracts platform differences
- **Path Handling**: `pathlib.Path` for cross-platform path operations

## Performance Characteristics

- **Search**: Target <5s for 10,000-file codebases (ripgrep performance)
- **Process Listing**: Target <2s (psutil iteration)
- **Timeout Accuracy**: Within 100ms of configured value

## Testing Strategy

### Unit Tests
- Mocked subprocess and psutil calls
- Focus on logic, error handling, edge cases
- Fast execution for TDD workflow

### Integration Tests
- Real ripgrep execution with test fixtures
- Safe commands only (echo, sleep)
- Verifies actual tool behavior

### Security Tests
- Path traversal attack scenarios
- Injection prevention validation
- Resource limit enforcement
- Error message sanitization checks

## Deployment

- No containerization required (local MCP server)
- Installed via Claude Desktop configuration
- Runs in user context (no elevated permissions needed)
- Configured via environment variables in Claude config

## Future Considerations

- **US2 (execute_command)**: Command execution with subprocess
- **US3 (list_processes)**: Process listing with psutil
- **US4 (kill_process)**: Process termination with psutil

See [tasks.md](../specs/001-procexec-mcp-server/tasks.md) for incremental delivery plan.
