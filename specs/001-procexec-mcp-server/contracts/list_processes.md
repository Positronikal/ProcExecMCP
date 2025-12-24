# Tool Contract: list_processes

## Overview

List running processes with optional filtering by name, sorting, and result limiting. Returns process information including PID, name, CPU, memory, and command line.

**Tool Name**: `list_processes`
**Category**: Process Management
**Priority**: P2

---

## Input Schema

```json
{
  "type": "object",
  "properties": {
    "name_filter": {
      "type": "string",
      "description": "Filter processes by name (case-insensitive substring match). If null, list all processes.",
      "default": null,
      "maxLength": 256,
      "examples": ["python", "node", "chrome"]
    },
    "sort_by": {
      "type": "string",
      "description": "Sort processes by: 'cpu', 'memory', 'pid', or 'name'",
      "default": "cpu",
      "enum": ["cpu", "memory", "pid", "name"]
    },
    "limit": {
      "type": "integer",
      "description": "Maximum number of processes to return",
      "default": 100,
      "minimum": 1,
      "maximum": 1000
    }
  }
}
```

---

## Output Schema

```json
{
  "type": "object",
  "properties": {
    "processes": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "pid": {
            "type": "integer",
            "description": "Process ID",
            "minimum": 1
          },
          "name": {
            "type": "string",
            "description": "Process name"
          },
          "cpu_percent": {
            "type": "number",
            "description": "CPU usage percentage",
            "minimum": 0.0
          },
          "memory_mb": {
            "type": "number",
            "description": "Memory usage in megabytes",
            "minimum": 0.0
          },
          "cmdline": {
            "type": "string",
            "description": "Full command line used to start the process"
          },
          "status": {
            "type": "string",
            "description": "Process status (running, sleeping, zombie, etc.)"
          }
        },
        "required": ["pid", "name", "cpu_percent", "memory_mb", "cmdline", "status"]
      },
      "description": "List of processes matching the filter criteria"
    },
    "total_count": {
      "type": "integer",
      "description": "Total number of matching processes (may exceed returned if limited)",
      "minimum": 0
    },
    "truncated": {
      "type": "boolean",
      "description": "Whether the process list was truncated due to limit"
    },
    "retrieval_time_ms": {
      "type": "integer",
      "description": "Time taken to retrieve process information in milliseconds",
      "minimum": 0
    }
  },
  "required": ["processes", "total_count", "truncated", "retrieval_time_ms"]
}
```

---

## Error Conditions

| Error Category | Condition | Message |
|----------------|-----------|---------|
| `validation` | Invalid sort_by value | "Invalid sort field" |
| `permission` | Insufficient permissions | "Permission denied to access process information" |
| `system` | Process access error | "Failed to retrieve process information" |

---

## Usage Example

**Request**:
```json
{
  "name_filter": "python",
  "sort_by": "memory",
  "limit": 50
}
```

**Response**:
```json
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
  "truncated": false,
  "retrieval_time_ms": 45
}
```
