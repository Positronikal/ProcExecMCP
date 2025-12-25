# Tool Contract: kill_process

## Overview

Terminate a process by PID with optional forced termination. Supports graceful termination (SIGTERM/WM_CLOSE) and forced termination (SIGKILL/TerminateProcess).

**Tool Name**: `kill_process`
**Category**: Process Management
**Priority**: P3

---

## Input Schema

```json
{
  "type": "object",
  "properties": {
    "pid": {
      "type": "integer",
      "description": "Process ID to terminate",
      "minimum": 1,
      "examples": [1234, 5678]
    },
    "force": {
      "type": "boolean",
      "description": "Force termination (SIGKILL/TerminateProcess) instead of graceful (SIGTERM/WM_CLOSE)",
      "default": false
    },
    "timeout_seconds": {
      "type": "integer",
      "description": "Timeout in seconds to wait for process termination",
      "default": 5,
      "minimum": 1,
      "maximum": 60
    }
  },
  "required": ["pid"]
}
```

---

## Output Schema

```json
{
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean",
      "description": "Whether the process was successfully terminated"
    },
    "pid": {
      "type": "integer",
      "description": "Process ID that was targeted",
      "minimum": 1
    },
    "message": {
      "type": "string",
      "description": "Human-readable status message"
    },
    "termination_time_ms": {
      "type": "integer",
      "description": "Time taken to terminate process in milliseconds",
      "minimum": 0
    },
    "forced": {
      "type": "boolean",
      "description": "Whether forced termination (SIGKILL) was used"
    }
  },
  "required": ["success", "pid", "message", "termination_time_ms", "forced"]
}
```

---

## Error Conditions

| Error Category | Condition | Message |
|----------------|-----------|---------|
| `validation` | Invalid PID (≤0) | "Invalid process ID" |
| `not_found` | Process does not exist | "Process {pid} does not exist" |
| `permission` | Insufficient permissions | "Permission denied to terminate process {pid}" |
| `timeout` | Process didn't terminate within timeout | "Process {pid} did not terminate within timeout" |
| `system` | Termination failed | "Failed to terminate process {pid}" |

---

## Usage Example

**Request**:
```json
{
  "pid": 1234,
  "force": false,
  "timeout_seconds": 5
}
```

**Response**:
```json
{
  "success": true,
  "pid": 1234,
  "message": "Process 1234 (python.exe) terminated successfully",
  "termination_time_ms": 150,
  "forced": false
}
```

---

## Termination Modes

### Graceful Termination (default)
- **Windows**: Sends WM_CLOSE message
- **Unix**: Sends SIGTERM signal
- Allows process to clean up resources
- Waits for timeout period

### Forced Termination (force=true)
- **Windows**: Calls TerminateProcess
- **Unix**: Sends SIGKILL signal
- Immediate termination, no cleanup
- Use when graceful termination fails

---

## Security Considerations

1. **Permission Checks**: Validates caller has permission to terminate process
2. **System Process Protection**: Blocking termination of critical system processes should be handled at system level
3. **Configuration**: Can be disabled via `PROCEXEC_ENABLE_KILL=false` environment variable
