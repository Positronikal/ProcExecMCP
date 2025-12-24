# Research: ProcExecMCP Implementation

**Feature**: ProcExecMCP Server
**Date**: 2025-12-23
**Status**: Complete

## Overview

This document consolidates research findings for implementing ProcExecMCP, a stateless command execution and process management MCP server. All technical unknowns from the planning phase have been resolved.

---

## 1. FastMCP Tool Implementation Patterns

**Question**: What are the best practices for implementing MCP tools with FastMCP, particularly for structured output and error handling?

**Decision**: Use FastMCP decorator pattern with Pydantic models for structured output

**Rationale**:
- FastMCP provides `@mcp.tool()` decorator that automatically handles MCP protocol compliance
- Pydantic models as return types enable structured output with automatic schema generation
- Context parameter injection provides access to logging, progress reporting, and error handling
- `CallToolResult` can be returned directly for full control including `_meta` field

**Implementation Pattern**:
```python
from mcp.server.fastmcp import FastMCP, Context
from pydantic import BaseModel, Field

mcp = FastMCP("ProcExecMCP", json_response=True, stateless_http=True)

class SearchResult(BaseModel):
    file_path: str = Field(description="Path to file containing match")
    line_number: int = Field(description="Line number of match")
    line_text: str = Field(description="Matched line content")
    context_before: list[str] = Field(description="Lines before match")
    context_after: list[str] = Field(description="Lines after match")

@mcp.tool()
async def search_file_contents(
    pattern: str,
    path: str,
    case_sensitive: bool = True,
    ctx: Context | None = None
) -> list[SearchResult]:
    """Search for pattern in files"""
    # Implementation with automatic validation and structured output
    if ctx:
        await ctx.info(f"Searching for '{pattern}' in {path}")
    # ... implementation
    return results
```

**Alternatives Considered**:
- Low-level MCP server implementation: Rejected due to boilerplate overhead and manual protocol handling
- Unstructured text output: Rejected as it loses type safety and makes client-side parsing difficult
- No context parameter: Rejected as it prevents progress reporting and structured logging

**References**:
- FastMCP README: D:\dev\ARTIFICIAL_INTELLIGENCE\MCP\_MCP-Tools-Dev\python-sdk\README.md (lines 140-150)
- Structured output examples: D:\dev\ARTIFICIAL_INTELLIGENCE\MCP\_MCP-Tools-Dev\python-sdk\README.md (lines 454-556)
- Tool with context: D:\dev\ARTIFICIAL_INTELLIGENCE\MCP\_MCP-Tools-Dev\python-sdk\README.md (lines 340-365)

---

## 2. Subprocess Security Best Practices

**Question**: How do we prevent shell injection while supporting flexible command execution across Windows and Unix platforms?

**Decision**: Use subprocess with argument lists and platform-specific command parsing

**Rationale**:
- Never use `shell=True` - it enables shell injection vulnerabilities
- Pass commands as argument lists: `subprocess.run(['cmd', 'arg1', 'arg2'])`
- For Windows: Use `shlex.split()` with `posix=False` to parse command strings into argument lists
- For Unix: Use `shlex.split()` with `posix=True` for proper shell quoting
- Enforce timeout via `subprocess.run(timeout=seconds)`
- Capture output with `capture_output=True` and validate size limits

**Implementation Pattern**:
```python
import subprocess
import shlex
import platform

def execute_command_safely(command_str: str, cwd: str | None, timeout: int) -> tuple[str, str, int]:
    """Execute command safely without shell injection risk"""
    # Parse command string into argument list based on platform
    is_windows = platform.system() == "Windows"
    args = shlex.split(command_str, posix=not is_windows)

    # Execute with strict security parameters
    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=cwd,
        shell=False,  # CRITICAL: Never use shell=True
        check=False   # Don't raise on non-zero exit
    )

    return result.stdout, result.stderr, result.returncode
```

**Alternatives Considered**:
- Allow `shell=True` with input sanitization: Rejected as sanitization is error-prone and bypassable
- Restrict to pre-approved command whitelist: Rejected as it defeats the purpose of flexible command execution for architectural review
- Use Windows-only or Unix-only APIs: Rejected as cross-platform compatibility is a requirement

**Security Validation**:
- Test with injection attempts: `"; rm -rf /"`, `"| cat /etc/passwd"`, `"&& format C:"`
- Verify timeout enforcement prevents infinite loops
- Confirm output size limits prevent memory exhaustion
- Validate that command parsing handles edge cases (quotes, backslashes, spaces)

**References**:
- Python subprocess security: https://docs.python.org/3/library/subprocess.html#security-considerations
- shlex for safe parsing: https://docs.python.org/3/library/shlex.html

---

## 3. Ripgrep Integration for File Search

**Question**: What are the optimal ripgrep parameters for architectural code review, and how do we invoke it safely via subprocess?

**Decision**: Invoke system ripgrep binary via subprocess with structured JSON output

**Rationale**:
- Ripgrep (`rg`) is purpose-built for fast code search, significantly faster than pure Python solutions
- JSON output (`--json`) provides structured results that are easy to parse
- System binary invocation avoids Python ripgrep library dependency (keeps dependency count low)
- Ripgrep handles gitignore, exclusions, and context lines natively

**Implementation Pattern**:
```python
import subprocess
import json
from pathlib import Path

def search_with_ripgrep(pattern: str, path: str, case_sensitive: bool, context_lines: int = 2) -> list[dict]:
    """Search using system ripgrep binary"""
    args = [
        "rg",
        "--json",                    # Structured JSON output
        "--context", str(context_lines),  # Lines before/after match
        "--line-number",             # Include line numbers
        "--no-heading",              # Format for JSON parsing
        "--color", "never",          # No ANSI color codes
    ]

    if not case_sensitive:
        args.append("--ignore-case")

    args.extend([pattern, path])

    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
        timeout=30,
        shell=False
    )

    # Parse JSON lines output
    matches = []
    for line in result.stdout.splitlines():
        if line.strip():
            data = json.loads(line)
            if data.get("type") == "match":
                matches.append(data["data"])

    return matches
```

**Ripgrep Parameters**:
- `--json`: Structured output for reliable parsing
- `--context N`: Include N lines before/after match
- `--line-number`: Essential for matching line numbers to code
- `--ignore-case`: Case-insensitive search option
- `--type-add`, `--type`: File type filtering (e.g., python, js)
- `--max-filesize`: Prevent searching huge files
- `--max-count`: Limit matches per file

**Alternatives Considered**:
- Pure Python search (using `re` module): Rejected due to poor performance on large codebases
- Python ripgrep bindings: Rejected to minimize dependencies
- Alternative search tools (ag, ack): Rejected as ripgrep is faster and more widely available

**Error Handling**:
- Check if `rg` binary exists before invocation
- Handle ripgrep exit codes: 0 (matches found), 1 (no matches), 2 (error)
- Provide clear error message if ripgrep not installed

**References**:
- Ripgrep user guide: https://github.com/BurntSushi/ripgrep/blob/master/GUIDE.md
- JSON output format: https://docs.rs/grep-printer/latest/grep_printer/struct.JSON.html

---

## 4. psutil for Cross-Platform Process Management

**Question**: How do we reliably list and manage processes across Windows and Unix using psutil?

**Decision**: Use psutil process iteration with exception handling for permission denied

**Rationale**:
- psutil provides consistent cross-platform API for process information
- Handles platform differences (Windows vs Unix) transparently
- Provides rich process metadata: PID, name, CPU, memory, command line
- Graceful handling of processes that terminate during iteration

**Implementation Pattern**:
```python
import psutil
from dataclasses import dataclass

@dataclass
class ProcessInfo:
    pid: int
    name: str
    cpu_percent: float
    memory_mb: float
    cmdline: str

def list_processes(name_filter: str | None = None) -> list[ProcessInfo]:
    """List running processes with optional name filtering"""
    processes = []

    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # Get process info atomically
            info = proc.info

            # Apply name filter if provided
            if name_filter and name_filter.lower() not in info['name'].lower():
                continue

            # Get CPU and memory (may require brief measurement)
            cpu = proc.cpu_percent(interval=0.1)
            memory = proc.memory_info().rss / (1024 * 1024)  # Convert to MB

            processes.append(ProcessInfo(
                pid=info['pid'],
                name=info['name'],
                cpu_percent=cpu,
                memory_mb=round(memory, 2),
                cmdline=' '.join(info['cmdline'] or [])
            ))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            # Process terminated or no permission - skip gracefully
            continue

    return processes

def kill_process(pid: int, force: bool = False) -> bool:
    """Terminate process by PID"""
    try:
        proc = psutil.Process(pid)
        if force:
            proc.kill()  # SIGKILL / TerminateProcess
        else:
            proc.terminate()  # SIGTERM / WM_CLOSE
        proc.wait(timeout=5)  # Wait for termination
        return True
    except psutil.NoSuchProcess:
        raise ValueError(f"Process {pid} does not exist")
    except psutil.AccessDenied:
        raise PermissionError(f"Permission denied to terminate process {pid}")
    except psutil.TimeoutExpired:
        # Process didn't terminate, may need force kill
        return False
```

**psutil Key APIs**:
- `psutil.process_iter()`: Iterate all processes
- `Process.pid`: Process ID
- `Process.name()`: Process name
- `Process.cpu_percent()`: CPU usage percentage
- `Process.memory_info()`: Memory usage details
- `Process.cmdline()`: Full command line
- `Process.terminate()`: Graceful termination (SIGTERM)
- `Process.kill()`: Forced termination (SIGKILL)

**Alternatives Considered**:
- Platform-specific APIs (Windows tasklist, Unix ps): Rejected due to complexity and parsing overhead
- Manual /proc filesystem reading on Unix: Rejected as psutil provides better abstraction
- WMI on Windows: Rejected as psutil is simpler and cross-platform

**Error Handling**:
- `NoSuchProcess`: Process terminated between iteration and access
- `AccessDenied`: Insufficient permissions to access process
- `ZombieProcess`: Process is in zombie state (Unix)
- `TimeoutExpired`: Process didn't terminate within timeout

**References**:
- psutil documentation: https://psutil.readthedocs.io/en/latest/
- Process class API: https://psutil.readthedocs.io/en/latest/#psutil.Process

---

## 5. Input Validation and Path Security

**Question**: How do we prevent path traversal attacks while allowing flexible file system access for code review?

**Decision**: Validate paths using `pathlib.Path.resolve()` and reject suspicious patterns

**Rationale**:
- `Path.resolve()` resolves symlinks and normalizes paths to absolute form
- Detect path traversal attempts by checking for `..` components after resolution
- Validate that paths exist before operations
- Reject paths to sensitive system directories (configurable blocklist)

**Implementation Pattern**:
```python
from pathlib import Path
import os

SENSITIVE_PATHS = [
    "/etc/shadow",
    "/etc/passwd",
    "C:\\Windows\\System32\\config",
    "C:\\Windows\\System32\\drivers",
]

def validate_path(path_str: str, must_exist: bool = True) -> Path:
    """Validate path for security and existence"""
    try:
        # Resolve to absolute path
        path = Path(path_str).resolve(strict=False)

        # Check if path exists (if required)
        if must_exist and not path.exists():
            raise ValueError(f"Path does not exist: {path}")

        # Check for traversal attempts
        path_parts = path.parts
        if ".." in path_parts:
            raise ValueError(f"Path traversal not allowed: {path}")

        # Check against sensitive paths
        path_str_normalized = str(path).lower()
        for sensitive in SENSITIVE_PATHS:
            if path_str_normalized.startswith(sensitive.lower()):
                raise ValueError(f"Access to sensitive path not allowed: {path}")

        return path
    except (OSError, ValueError) as e:
        raise ValueError(f"Invalid path: {e}")

def validate_directory(path_str: str) -> Path:
    """Validate that path is a directory"""
    path = validate_path(path_str, must_exist=True)
    if not path.is_dir():
        raise ValueError(f"Path is not a directory: {path}")
    return path

def validate_file(path_str: str) -> Path:
    """Validate that path is a file"""
    path = validate_path(path_str, must_exist=True)
    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")
    return path
```

**Security Checks**:
- Path normalization to prevent `./../../etc/passwd` style attacks
- Symlink resolution to prevent symlink-based access to restricted areas
- Existence validation to prevent operations on non-existent paths
- Sensitive path blocklist (configurable, with defaults for system paths)

**Alternatives Considered**:
- Whitelist allowed directories: Rejected as it's too restrictive for code review use case
- No path validation: Rejected due to security risk
- Regex-based validation: Rejected as it's error-prone compared to path resolution

**Configurable Blocklist**:
- Environment variable: `PROCEXEC_BLOCKED_PATHS` (comma-separated)
- Default blocklist includes system directories, credential files, and device files

**References**:
- pathlib documentation: https://docs.python.org/3/library/pathlib.html
- OWASP Path Traversal: https://owasp.org/www-community/attacks/Path_Traversal

---

## 6. Error Handling and Sanitization

**Question**: How do we provide useful error messages to Claude without leaking sensitive system information?

**Decision**: Sanitize error messages to remove absolute paths, usernames, and internal details

**Rationale**:
- LLMs can make better decisions with clear error messages
- Absolute paths can leak system structure and usernames
- Stack traces can expose implementation details
- Sanitized errors maintain utility while improving security

**Implementation Pattern**:
```python
import re
from pathlib import Path

def sanitize_path(path_str: str) -> str:
    """Replace absolute path with relative or basename"""
    try:
        path = Path(path_str)
        # Return just the filename or last component
        return path.name or str(path)
    except:
        return "[path]"

def sanitize_error_message(message: str) -> str:
    """Remove sensitive information from error messages"""
    # Remove absolute paths (Windows and Unix)
    message = re.sub(r'[A-Z]:\\[^\\s]+', sanitize_path, message)
    message = re.sub(r'/(?:home|root|Users)/[^\\s]+', sanitize_path, message)

    # Remove usernames
    message = re.sub(r'user\\s+[\\w]+', 'user [redacted]', message, flags=re.IGNORECASE)

    # Remove IP addresses
    message = re.sub(r'\\b\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\b', '[IP]', message)

    return message

class SanitizedError(Exception):
    """Exception with sanitized message"""
    def __init__(self, message: str, original_error: Exception | None = None):
        sanitized = sanitize_error_message(message)
        super().__init__(sanitized)
        self.original_error = original_error

# Usage in tool functions
try:
    result = execute_command(cmd, cwd, timeout)
except subprocess.TimeoutExpired:
    raise SanitizedError("Command exceeded timeout limit")
except PermissionError as e:
    raise SanitizedError("Permission denied for operation")
except Exception as e:
    raise SanitizedError(f"Operation failed: {type(e).__name__}")
```

**Sanitization Rules**:
- Replace absolute paths with basenames
- Redact usernames and home directories
- Remove IP addresses and hostnames
- Suppress stack traces in production
- Generic error categories instead of specific system errors

**Error Message Guidelines**:
- Include error category (timeout, permission, not found)
- Include operation context (command, path, PID)
- Omit system-specific details (absolute paths, internal IDs)
- Suggest corrective action when possible

**Alternatives Considered**:
- No sanitization: Rejected due to information leakage risk
- Complete error suppression: Rejected as it prevents Claude from making informed decisions
- Per-error-type sanitization: Selected approach uses general pattern matching

**References**:
- OWASP Information Leakage: https://owasp.org/www-community/vulnerabilities/Information_exposure

---

## 7. Configuration via Environment Variables

**Question**: How should timeout, output limits, and other security parameters be configurable?

**Decision**: Use environment variables with sensible defaults, validated at startup

**Rationale**:
- Environment variables are standard for MCP server configuration
- Allows per-deployment customization without code changes
- Claude Desktop configuration can set environment variables
- Validation at startup prevents runtime configuration errors

**Configuration Design**:
```python
import os
from dataclasses import dataclass

@dataclass
class ServerConfig:
    """Server configuration from environment variables"""
    timeout_ms: int = 30000  # Default 30 seconds
    max_output_bytes: int = 10 * 1024 * 1024  # Default 10MB
    blocked_paths: list[str] = None
    enable_process_kill: bool = True

    @classmethod
    def from_environment(cls) -> "ServerConfig":
        """Load configuration from environment variables"""
        timeout_ms = int(os.getenv("PROCEXEC_TIMEOUT", "30000"))
        max_output = int(os.getenv("PROCEXEC_MAX_OUTPUT", str(10 * 1024 * 1024)))
        blocked = os.getenv("PROCEXEC_BLOCKED_PATHS", "").split(",")
        blocked_paths = [p.strip() for p in blocked if p.strip()]
        enable_kill = os.getenv("PROCEXEC_ENABLE_KILL", "true").lower() == "true"

        # Validation
        if timeout_ms < 1000 or timeout_ms > 300000:
            raise ValueError("PROCEXEC_TIMEOUT must be between 1000 and 300000 ms")
        if max_output < 1024 or max_output > 100 * 1024 * 1024:
            raise ValueError("PROCEXEC_MAX_OUTPUT must be between 1KB and 100MB")

        return cls(
            timeout_ms=timeout_ms,
            max_output_bytes=max_output,
            blocked_paths=blocked_paths,
            enable_process_kill=enable_kill
        )

# Usage in server.py
config = ServerConfig.from_environment()
```

**Environment Variables**:
- `PROCEXEC_TIMEOUT`: Command timeout in milliseconds (default: 30000)
- `PROCEXEC_MAX_OUTPUT`: Maximum output size in bytes (default: 10485760)
- `PROCEXEC_BLOCKED_PATHS`: Comma-separated list of blocked paths (default: system paths)
- `PROCEXEC_ENABLE_KILL`: Enable process termination tool (default: true)

**Claude Desktop Configuration Example**:
```json
{
  "mcpServers": {
    "procexec": {
      "command": "uv",
      "args": ["--directory", "D:\\dev\\ARTIFICIAL_INTELLIGENCE\\MCP\\ProcExecMCP", "run", "procexec"],
      "env": {
        "PROCEXEC_TIMEOUT": "30000",
        "PROCEXEC_MAX_OUTPUT": "10485760",
        "PROCEXEC_BLOCKED_PATHS": "C:\\Windows\\System32\\config,/etc/shadow"
      }
    }
  }
}
```

**Alternatives Considered**:
- Configuration file (JSON/YAML): Rejected as environment variables are simpler and match MCP conventions
- Hard-coded values: Rejected due to lack of deployment flexibility
- Command-line arguments: Rejected as MCP servers are invoked without user interaction

**References**:
- MCP server configuration: https://modelcontextprotocol.io/quickstart/server
- Twelve-Factor App config: https://12factor.net/config

---

## 8. Testing Strategy

**Question**: How do we achieve >80% code coverage while testing security-critical functionality safely?

**Decision**: Three-tier testing approach: unit (mocked), integration (safe commands), security (attack scenarios)

**Rationale**:
- Unit tests with mocking avoid dangerous operations and enable fast iteration
- Integration tests with safe commands validate real-world behavior
- Security tests explicitly validate attack prevention
- Pytest fixtures provide consistent test setup

**Testing Architecture**:

**Unit Tests (Mocked)**:
```python
# tests/unit/test_execute.py
import pytest
from unittest.mock import patch, MagicMock
from procexec.tools.execute import execute_command

@pytest.fixture
def mock_subprocess():
    with patch('subprocess.run') as mock:
        mock.return_value = MagicMock(
            stdout="output",
            stderr="",
            returncode=0
        )
        yield mock

def test_execute_command_basic(mock_subprocess):
    """Test basic command execution"""
    stdout, stderr, code = execute_command("echo test", None, 30)

    assert mock_subprocess.called
    # Verify subprocess called with correct parameters
    args, kwargs = mock_subprocess.call_args
    assert kwargs['shell'] == False
    assert kwargs['timeout'] == 30
    assert stdout == "output"
```

**Integration Tests (Safe Commands)**:
```python
# tests/integration/test_execute_integration.py
import pytest
from procexec.tools.execute import execute_command

def test_execute_echo_command():
    """Test execution with real echo command"""
    stdout, stderr, code = execute_command("echo test", None, 30)
    assert "test" in stdout
    assert code == 0

def test_execute_with_timeout():
    """Test timeout enforcement with sleep command"""
    with pytest.raises(TimeoutError):
        # Platform-specific sleep command
        import platform
        if platform.system() == "Windows":
            execute_command("timeout 5", None, 1)  # Sleep 5s, timeout 1s
        else:
            execute_command("sleep 5", None, 1)
```

**Security Tests (Attack Scenarios)**:
```python
# tests/security/test_injection.py
import pytest
from procexec.tools.execute import execute_command
from procexec.utils.validation import validate_path

def test_command_injection_prevention():
    """Test that command injection attempts are blocked"""
    dangerous_commands = [
        "; rm -rf /",
        "| cat /etc/passwd",
        "&& format C:",
        "$(malicious command)",
        "`malicious command`"
    ]

    for cmd in dangerous_commands:
        with pytest.raises((ValueError, SecurityError)):
            execute_command(cmd, None, 30)

def test_path_traversal_prevention():
    """Test that path traversal is blocked"""
    dangerous_paths = [
        "../../../etc/passwd",
        "..\\..\\..\\Windows\\System32\\config",
        "/etc/shadow",
        "C:\\Windows\\System32\\config\\SAM"
    ]

    for path in dangerous_paths:
        with pytest.raises(ValueError):
            validate_path(path)

def test_output_size_limit():
    """Test that output size limits are enforced"""
    # Generate large output command
    import platform
    if platform.system() == "Windows":
        cmd = "for /L %i in (1,1,1000000) do @echo Line %i"
    else:
        cmd = "yes | head -n 1000000"

    with pytest.raises(MemoryError):
        execute_command(cmd, None, 30)
```

**Test Coverage Goals**:
- Unit tests: All tool functions, utilities, platform abstraction
- Integration tests: Happy paths with safe commands
- Security tests: All attack vectors and security requirements
- Target: >80% overall coverage, 100% coverage of security-critical code

**Pytest Configuration** (pyproject.toml):
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--cov=src/procexec",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--cov-fail-under=80"
]
```

**Alternatives Considered**:
- Only integration tests: Rejected due to slow execution and difficulty testing error paths
- No security tests: Rejected as security is critical requirement
- 100% coverage requirement: Rejected as diminishing returns, 80% is pragmatic

**References**:
- pytest documentation: https://docs.pytest.org/
- pytest-cov: https://pytest-cov.readthedocs.io/

---

## Summary of Key Decisions

| Area | Decision | Rationale |
|------|----------|-----------|
| **MCP Framework** | FastMCP with structured output | Automatic protocol handling, type safety, less boilerplate |
| **Security** | subprocess with argument lists, no shell=True | Prevents shell injection vulnerabilities |
| **Search** | System ripgrep via subprocess with JSON output | Fast, structured results, minimal dependencies |
| **Process Management** | psutil with exception handling | Cross-platform, consistent API, graceful error handling |
| **Path Validation** | pathlib resolution + traversal detection | Prevents path traversal attacks while allowing flexibility |
| **Error Handling** | Sanitized messages removing sensitive data | Useful errors without information leakage |
| **Configuration** | Environment variables with validation | Standard MCP pattern, deployment flexibility |
| **Testing** | Three-tier: unit (mocked), integration (safe), security (attacks) | Comprehensive coverage, fast iteration, security validation |

---

## Implementation Readiness

All technical unknowns have been resolved. The implementation can proceed with:
1. High confidence in security approach
2. Clear patterns for each tool
3. Well-defined testing strategy
4. Validated technology choices

**Status**: ✓ COMPLETE - Ready for Phase 1 (Design & Contracts)
