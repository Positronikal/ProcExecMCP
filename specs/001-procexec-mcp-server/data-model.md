# Data Model: ProcExecMCP

**Feature**: ProcExecMCP Server
**Date**: 2025-12-23
**Status**: Complete

## Overview

This document defines the data models (Pydantic schemas) for all tool inputs and outputs in ProcExecMCP. Since the server is stateless, there are no persistent entities - only request/response models for the 4 MCP tools.

---

## Input Schemas (Tool Parameters)

### 1. SearchFileContentsInput

**Tool**: `search_file_contents`
**Purpose**: Input validation for file content search operations

```python
from pydantic import BaseModel, Field
from pathlib import Path

class SearchFileContentsInput(BaseModel):
    """Input schema for search_file_contents tool"""

    pattern: str = Field(
        description="Regular expression pattern to search for",
        min_length=1,
        max_length=1000,
        examples=["TODO", "def\\s+\\w+", "import\\s+\\w+"]
    )

    path: str = Field(
        description="File or directory path to search in",
        examples=["C:\\projects\\myapp", "/home/user/code", "./src"]
    )

    case_sensitive: bool = Field(
        default=True,
        description="Whether the search should be case-sensitive"
    )

    file_types: list[str] | None = Field(
        default=None,
        description="File type filters (e.g., ['py', 'js', 'ts']). If None, search all files.",
        examples=[["py", "pyi"], ["js", "ts", "tsx"]]
    )

    exclude_patterns: list[str] | None = Field(
        default=None,
        description="Glob patterns to exclude (e.g., ['*.min.js', 'node_modules'])",
        examples=[["node_modules", "*.min.js"], ["venv", "__pycache__"]]
    )

    max_results: int = Field(
        default=1000,
        description="Maximum number of match results to return",
        ge=1,
        le=10000
    )

    context_lines: int = Field(
        default=2,
        description="Number of lines to include before and after each match",
        ge=0,
        le=10
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "pattern": "TODO",
                    "path": "./src",
                    "case_sensitive": False,
                    "file_types": ["py"],
                    "exclude_patterns": ["test_*.py"],
                    "max_results": 100,
                    "context_lines": 2
                }
            ]
        }
```

**Validation Rules**:
- `pattern`: Non-empty, max 1000 chars (prevent regex DoS)
- `path`: Validated via `validate_path()` utility (see validation.py)
- `case_sensitive`: Boolean flag
- `file_types`: Optional list of file extensions
- `exclude_patterns`: Optional list of glob patterns
- `max_results`: Between 1 and 10,000 (prevent memory exhaustion)
- `context_lines`: Between 0 and 10 (reasonable context)

---

### 2. ExecuteCommandInput

**Tool**: `execute_command`
**Purpose**: Input validation for command execution

```python
from pydantic import BaseModel, Field, field_validator

class ExecuteCommandInput(BaseModel):
    """Input schema for execute_command tool"""

    command: str = Field(
        description="Command to execute (will be parsed into argument list for security)",
        min_length=1,
        max_length=5000,
        examples=["python --version", "npm test", "git status"]
    )

    working_directory: str | None = Field(
        default=None,
        description="Working directory for command execution. If None, uses current directory.",
        examples=["C:\\projects\\myapp", "/home/user/code"]
    )

    timeout_ms: int = Field(
        default=30000,
        description="Timeout in milliseconds (overrides server default)",
        ge=1000,
        le=300000  # Max 5 minutes
    )

    capture_output: bool = Field(
        default=True,
        description="Whether to capture stdout and stderr"
    )

    @field_validator('command')
    @classmethod
    def validate_command_not_empty(cls, v: str) -> str:
        """Ensure command is not just whitespace"""
        if not v.strip():
            raise ValueError("Command cannot be empty or whitespace")
        return v.strip()

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "command": "python -m pytest tests/",
                    "working_directory": "./myproject",
                    "timeout_ms": 60000,
                    "capture_output": True
                }
            ]
        }
```

**Validation Rules**:
- `command`: Non-empty string, max 5000 chars
- `working_directory`: Validated via `validate_directory()` if provided
- `timeout_ms`: Between 1s and 5 minutes (prevents runaway processes)
- `capture_output`: Boolean flag

**Security Note**: Command is parsed into argument list using `shlex.split()` to prevent shell injection.

---

### 3. ListProcessesInput

**Tool**: `list_processes`
**Purpose**: Input validation for process listing

```python
from pydantic import BaseModel, Field

class ListProcessesInput(BaseModel):
    """Input schema for list_processes tool"""

    name_filter: str | None = Field(
        default=None,
        description="Filter processes by name (case-insensitive substring match). If None, list all processes.",
        max_length=256,
        examples=["python", "node", "chrome"]
    )

    sort_by: str = Field(
        default="cpu",
        description="Sort processes by: 'cpu', 'memory', 'pid', or 'name'",
        pattern="^(cpu|memory|pid|name)$"
    )

    limit: int = Field(
        default=100,
        description="Maximum number of processes to return",
        ge=1,
        le=1000
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "name_filter": "python",
                    "sort_by": "memory",
                    "limit": 50
                }
            ]
        }
```

**Validation Rules**:
- `name_filter`: Optional string, max 256 chars
- `sort_by`: Must be one of: cpu, memory, pid, name
- `limit`: Between 1 and 1000 (prevent excessive output)

---

### 4. KillProcessInput

**Tool**: `kill_process`
**Purpose**: Input validation for process termination

```python
from pydantic import BaseModel, Field

class KillProcessInput(BaseModel):
    """Input schema for kill_process tool"""

    pid: int = Field(
        description="Process ID to terminate",
        gt=0,
        examples=[1234, 5678]
    )

    force: bool = Field(
        default=False,
        description="Force termination (SIGKILL/TerminateProcess) instead of graceful (SIGTERM/WM_CLOSE)"
    )

    timeout_seconds: int = Field(
        default=5,
        description="Timeout in seconds to wait for process termination",
        ge=1,
        le=60
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "pid": 1234,
                    "force": False,
                    "timeout_seconds": 5
                }
            ]
        }
```

**Validation Rules**:
- `pid`: Positive integer (process IDs are always positive)
- `force`: Boolean flag for forced termination
- `timeout_seconds`: Between 1 and 60 seconds

---

## Output Schemas (Tool Results)

### 1. SearchMatch

**Tool**: `search_file_contents`
**Purpose**: Represents a single search match result

```python
from pydantic import BaseModel, Field

class SearchMatch(BaseModel):
    """Single search match result"""

    file_path: str = Field(
        description="Absolute path to file containing the match"
    )

    line_number: int = Field(
        description="Line number of the match (1-indexed)",
        ge=1
    )

    line_text: str = Field(
        description="Content of the matched line"
    )

    context_before: list[str] = Field(
        description="Lines before the match (for context)",
        default_factory=list
    )

    context_after: list[str] = Field(
        description="Lines after the match (for context)",
        default_factory=list
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "file_path": "/home/user/project/src/main.py",
                    "line_number": 42,
                    "line_text": "    # TODO: Implement error handling",
                    "context_before": [
                        "def process_data(data):",
                        "    result = transform(data)"
                    ],
                    "context_after": [
                        "    return result",
                        ""
                    ]
                }
            ]
        }
```

**Fields**:
- `file_path`: Sanitized absolute path
- `line_number`: 1-indexed line number
- `line_text`: The matched line content
- `context_before`: Up to N lines before match
- `context_after`: Up to N lines after match

---

### 2. SearchFileContentsOutput

**Tool**: `search_file_contents`
**Purpose**: Complete search results response

```python
from pydantic import BaseModel, Field

class SearchFileContentsOutput(BaseModel):
    """Output schema for search_file_contents tool"""

    matches: list[SearchMatch] = Field(
        description="List of search matches found"
    )

    total_matches: int = Field(
        description="Total number of matches found (may exceed returned matches if limited)",
        ge=0
    )

    files_searched: int = Field(
        description="Number of files searched",
        ge=0
    )

    truncated: bool = Field(
        description="Whether results were truncated due to max_results limit"
    )

    search_time_ms: int = Field(
        description="Time taken to complete search in milliseconds",
        ge=0
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "matches": [
                        {
                            "file_path": "/project/src/main.py",
                            "line_number": 42,
                            "line_text": "# TODO: Fix this",
                            "context_before": [],
                            "context_after": []
                        }
                    ],
                    "total_matches": 1,
                    "files_searched": 15,
                    "truncated": False,
                    "search_time_ms": 234
                }
            ]
        }
```

---

### 3. ExecuteCommandOutput

**Tool**: `execute_command`
**Purpose**: Command execution result

```python
from pydantic import BaseModel, Field

class ExecuteCommandOutput(BaseModel):
    """Output schema for execute_command tool"""

    stdout: str = Field(
        description="Standard output from the command"
    )

    stderr: str = Field(
        description="Standard error from the command"
    )

    exit_code: int = Field(
        description="Exit code returned by the command (0 typically means success)"
    )

    execution_time_ms: int = Field(
        description="Time taken to execute command in milliseconds",
        ge=0
    )

    timed_out: bool = Field(
        description="Whether the command was terminated due to timeout"
    )

    output_truncated: bool = Field(
        description="Whether output was truncated due to size limit"
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "stdout": "Python 3.11.5\\n",
                    "stderr": "",
                    "exit_code": 0,
                    "execution_time_ms": 123,
                    "timed_out": False,
                    "output_truncated": False
                }
            ]
        }
```

---

### 4. ProcessInfo

**Tool**: `list_processes`
**Purpose**: Information about a single process

```python
from pydantic import BaseModel, Field

class ProcessInfo(BaseModel):
    """Information about a running process"""

    pid: int = Field(
        description="Process ID",
        gt=0
    )

    name: str = Field(
        description="Process name"
    )

    cpu_percent: float = Field(
        description="CPU usage percentage",
        ge=0.0
    )

    memory_mb: float = Field(
        description="Memory usage in megabytes",
        ge=0.0
    )

    cmdline: str = Field(
        description="Full command line used to start the process"
    )

    status: str = Field(
        description="Process status (running, sleeping, zombie, etc.)"
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "pid": 1234,
                    "name": "python.exe",
                    "cpu_percent": 2.5,
                    "memory_mb": 125.3,
                    "cmdline": "python -m procexec",
                    "status": "running"
                }
            ]
        }
```

---

### 5. ListProcessesOutput

**Tool**: `list_processes`
**Purpose**: List of processes response

```python
from pydantic import BaseModel, Field

class ListProcessesOutput(BaseModel):
    """Output schema for list_processes tool"""

    processes: list[ProcessInfo] = Field(
        description="List of processes matching the filter criteria"
    )

    total_count: int = Field(
        description="Total number of matching processes (may exceed returned if limited)",
        ge=0
    )

    truncated: bool = Field(
        description="Whether the process list was truncated due to limit"
    )

    retrieval_time_ms: int = Field(
        description="Time taken to retrieve process information in milliseconds",
        ge=0
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "processes": [
                        {
                            "pid": 1234,
                            "name": "python.exe",
                            "cpu_percent": 2.5,
                            "memory_mb": 125.3,
                            "cmdline": "python -m procexec",
                            "status": "running"
                        }
                    ],
                    "total_count": 1,
                    "truncated": False,
                    "retrieval_time_ms": 45
                }
            ]
        }
```

---

### 6. KillProcessOutput

**Tool**: `kill_process`
**Purpose**: Process termination result

```python
from pydantic import BaseModel, Field

class KillProcessOutput(BaseModel):
    """Output schema for kill_process tool"""

    success: bool = Field(
        description="Whether the process was successfully terminated"
    )

    pid: int = Field(
        description="Process ID that was targeted",
        gt=0
    )

    message: str = Field(
        description="Human-readable status message"
    )

    termination_time_ms: int = Field(
        description="Time taken to terminate process in milliseconds",
        ge=0
    )

    forced: bool = Field(
        description="Whether forced termination (SIGKILL) was used"
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "success": True,
                    "pid": 1234,
                    "message": "Process 1234 (python.exe) terminated successfully",
                    "termination_time_ms": 150,
                    "forced": False
                }
            ]
        }
```

---

## Error Handling Models

### ToolError

**Purpose**: Standardized error response for tool execution failures

```python
from pydantic import BaseModel, Field
from enum import Enum

class ErrorCategory(str, Enum):
    """Error categories for tool failures"""
    VALIDATION = "validation"
    PERMISSION = "permission"
    NOT_FOUND = "not_found"
    TIMEOUT = "timeout"
    SECURITY = "security"
    SYSTEM = "system"
    UNKNOWN = "unknown"

class ToolError(BaseModel):
    """Standardized error response"""

    category: ErrorCategory = Field(
        description="Error category for programmatic handling"
    )

    message: str = Field(
        description="Sanitized, human-readable error message"
    )

    suggestion: str | None = Field(
        default=None,
        description="Optional suggestion for how to resolve the error"
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "category": "timeout",
                    "message": "Command exceeded timeout limit of 30 seconds",
                    "suggestion": "Try increasing the timeout_ms parameter or optimizing the command"
                }
            ]
        }
```

---

## State Transitions

**N/A** - ProcExecMCP is stateless. Each tool call is independent with no persistent state or state transitions between calls.

---

## Relationships

All models are independent with no relationships:
- **Input models**: Validated at tool invocation, discarded after processing
- **Output models**: Generated per tool execution, returned to client
- **Error models**: Generated on failure, returned to client

---

## Summary

| Model | Type | Purpose |
|-------|------|---------|
| `SearchFileContentsInput` | Input | Validate file search parameters |
| `SearchMatch` | Output | Individual search result |
| `SearchFileContentsOutput` | Output | Complete search results |
| `ExecuteCommandInput` | Input | Validate command execution parameters |
| `ExecuteCommandOutput` | Output | Command execution result |
| `ListProcessesInput` | Input | Validate process listing parameters |
| `ProcessInfo` | Output | Individual process information |
| `ListProcessesOutput` | Output | Complete process list |
| `KillProcessInput` | Input | Validate process termination parameters |
| `KillProcessOutput` | Output | Process termination result |
| `ToolError` | Error | Standardized error response |

All models use Pydantic for:
- Runtime type validation
- Automatic JSON schema generation for MCP protocol
- Clear documentation via Field descriptions
- Example generation for testing and documentation
