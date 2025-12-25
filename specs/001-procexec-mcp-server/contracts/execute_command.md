# Tool Contract: execute_command

## Overview

Execute commands safely with timeout enforcement and output size limits. Commands are parsed into argument lists to prevent shell injection.

**Tool Name**: `execute_command`
**Category**: Command Execution
**Priority**: P1 (Core functionality)

---

## Input Schema

```json
{
  "type": "object",
  "properties": {
    "command": {
      "type": "string",
      "description": "Command to execute (will be parsed into argument list for security)",
      "minLength": 1,
      "maxLength": 5000,
      "examples": ["python --version", "npm test", "git status"]
    },
    "working_directory": {
      "type": "string",
      "description": "Working directory for command execution. If null, uses current directory.",
      "default": null,
      "examples": ["C:\\projects\\myapp", "/home/user/code"]
    },
    "timeout_ms": {
      "type": "integer",
      "description": "Timeout in milliseconds (overrides server default)",
      "default": 30000,
      "minimum": 1000,
      "maximum": 300000
    },
    "capture_output": {
      "type": "boolean",
      "description": "Whether to capture stdout and stderr",
      "default": true
    }
  },
  "required": ["command"]
}
```

---

## Output Schema

```json
{
  "type": "object",
  "properties": {
    "stdout": {
      "type": "string",
      "description": "Standard output from the command"
    },
    "stderr": {
      "type": "string",
      "description": "Standard error from the command"
    },
    "exit_code": {
      "type": "integer",
      "description": "Exit code returned by the command (0 typically means success)"
    },
    "execution_time_ms": {
      "type": "integer",
      "description": "Time taken to execute command in milliseconds",
      "minimum": 0
    },
    "timed_out": {
      "type": "boolean",
      "description": "Whether the command was terminated due to timeout"
    },
    "output_truncated": {
      "type": "boolean",
      "description": "Whether output was truncated due to size limit"
    }
  },
  "required": ["stdout", "stderr", "exit_code", "execution_time_ms", "timed_out", "output_truncated"]
}
```

---

## Error Conditions

| Error Category | Condition | Message |
|----------------|-----------|---------|
| `validation` | Empty command | "Command cannot be empty" |
| `validation` | Working directory does not exist | "Working directory does not exist" |
| `security` | Shell injection attempt detected | "Invalid command format" |
| `timeout` | Command exceeds timeout | "Command exceeded timeout limit" |
| `permission` | Insufficient permissions | "Permission denied to execute command" |
| `system` | Command not found | "Command not found" |
| `system` | Execution error | "Command execution failed" |

---

## Usage Example

**Request**:
```json
{
  "command": "python -m pytest tests/",
  "working_directory": "./myproject",
  "timeout_ms": 60000,
  "capture_output": true
}
```

**Response**:
```json
{
  "stdout": "============================= test session starts ==============================\\n... 10 passed in 2.34s",
  "stderr": "",
  "exit_code": 0,
  "execution_time_ms": 2340,
  "timed_out": false,
  "output_truncated": false
}
```

---

## Security Guarantees

1. **No Shell Injection**: Commands parsed with `shlex.split()`, never use `shell=True`
2. **Timeout Enforcement**: Strict timeout prevents runaway processes
3. **Output Limiting**: Output size capped to prevent memory exhaustion
4. **Path Validation**: Working directory validated before execution
5. **Error Sanitization**: Error messages sanitized to prevent info leakage
