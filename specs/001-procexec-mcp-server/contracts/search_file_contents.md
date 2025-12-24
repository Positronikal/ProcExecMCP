# Tool Contract: search_file_contents

## Overview

Search for regex patterns in file contents across a directory or single file. Returns matches with line numbers and surrounding context.

**Tool Name**: `search_file_contents`
**Category**: Content Search
**Priority**: P1 (Core functionality)

---

## Input Schema

```json
{
  "type": "object",
  "properties": {
    "pattern": {
      "type": "string",
      "description": "Regular expression pattern to search for",
      "minLength": 1,
      "maxLength": 1000,
      "examples": ["TODO", "def\\s+\\w+", "import\\s+\\w+"]
    },
    "path": {
      "type": "string",
      "description": "File or directory path to search in",
      "examples": ["C:\\projects\\myapp", "/home/user/code", "./src"]
    },
    "case_sensitive": {
      "type": "boolean",
      "description": "Whether the search should be case-sensitive",
      "default": true
    },
    "file_types": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "File type filters (e.g., ['py', 'js', 'ts']). If null, search all files.",
      "default": null,
      "examples": [["py", "pyi"], ["js", "ts", "tsx"]]
    },
    "exclude_patterns": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "Glob patterns to exclude (e.g., ['*.min.js', 'node_modules'])",
      "default": null,
      "examples": [["node_modules", "*.min.js"], ["venv", "__pycache__"]]
    },
    "max_results": {
      "type": "integer",
      "description": "Maximum number of match results to return",
      "default": 1000,
      "minimum": 1,
      "maximum": 10000
    },
    "context_lines": {
      "type": "integer",
      "description": "Number of lines to include before and after each match",
      "default": 2,
      "minimum": 0,
      "maximum": 10
    }
  },
  "required": ["pattern", "path"]
}
```

---

## Output Schema

```json
{
  "type": "object",
  "properties": {
    "matches": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "file_path": {
            "type": "string",
            "description": "Absolute path to file containing the match"
          },
          "line_number": {
            "type": "integer",
            "description": "Line number of the match (1-indexed)",
            "minimum": 1
          },
          "line_text": {
            "type": "string",
            "description": "Content of the matched line"
          },
          "context_before": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Lines before the match (for context)"
          },
          "context_after": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Lines after the match (for context)"
          }
        },
        "required": ["file_path", "line_number", "line_text", "context_before", "context_after"]
      },
      "description": "List of search matches found"
    },
    "total_matches": {
      "type": "integer",
      "description": "Total number of matches found (may exceed returned matches if limited)",
      "minimum": 0
    },
    "files_searched": {
      "type": "integer",
      "description": "Number of files searched",
      "minimum": 0
    },
    "truncated": {
      "type": "boolean",
      "description": "Whether results were truncated due to max_results limit"
    },
    "search_time_ms": {
      "type": "integer",
      "description": "Time taken to complete search in milliseconds",
      "minimum": 0
    }
  },
  "required": ["matches", "total_matches", "files_searched", "truncated", "search_time_ms"]
}
```

---

## Error Conditions

| Error Category | Condition | HTTP Status | Message |
|----------------|-----------|-------------|---------|
| `validation` | Invalid regex pattern | 400 | "Invalid regular expression pattern: {details}" |
| `validation` | Path does not exist | 400 | "Search path does not exist" |
| `validation` | Invalid path (traversal attempt) | 400 | "Invalid search path" |
| `security` | Access to blocked path | 403 | "Access to path not allowed" |
| `timeout` | Search exceeds timeout | 408 | "Search operation exceeded timeout limit" |
| `system` | Ripgrep binary not found | 500 | "Search tool (ripgrep) not available on system" |
| `system` | Ripgrep execution error | 500 | "Search operation failed" |

---

## Usage Examples

### Example 1: Find all TODO comments in Python files

**Request**:
```json
{
  "pattern": "TODO|FIXME",
  "path": "./src",
  "case_sensitive": false,
  "file_types": ["py"],
  "max_results": 100,
  "context_lines": 2
}
```

**Response**:
```json
{
  "matches": [
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
  ],
  "total_matches": 1,
  "files_searched": 15,
  "truncated": false,
  "search_time_ms": 234
}
```

---

### Example 2: Find security vulnerabilities (SQL injection patterns)

**Request**:
```json
{
  "pattern": "execute\\(.*\\+.*\\)|cursor\\.execute\\(.*%",
  "path": "/home/user/webapp",
  "case_sensitive": true,
  "file_types": ["py"],
  "exclude_patterns": ["test_*.py", "venv"],
  "max_results": 50,
  "context_lines": 3
}
```

**Response**: (Similar structure to Example 1, with SQL injection matches)

---

### Example 3: Find all function definitions in TypeScript

**Request**:
```json
{
  "pattern": "function\\s+\\w+|const\\s+\\w+\\s*=\\s*\\(",
  "path": "./frontend/src",
  "case_sensitive": true,
  "file_types": ["ts", "tsx"],
  "exclude_patterns": ["*.test.ts", "node_modules"],
  "max_results": 500,
  "context_lines": 1
}
```

**Response**: (Similar structure with function definition matches)

---

## Implementation Notes

### Search Backend: Ripgrep

The tool uses system ripgrep binary (`rg`) for high-performance search:
- JSON output mode for structured parsing
- Respects `.gitignore` files by default
- Supports complex regex patterns
- Efficient handling of large codebases

### Path Validation

- All paths resolved to absolute paths
- Path traversal attempts (`..'` components) rejected
- Sensitive system paths blocked (configurable)
- Non-existent paths cause validation error

### Performance Characteristics

- Target: <5 seconds for 10,000-file codebases
- Timeout: Enforced at server level (default 30s)
- Result limiting prevents memory exhaustion
- Context lines kept minimal to control response size

### Security Considerations

1. **Regex Safety**: Pattern length limited to prevent ReDoS attacks
2. **Path Safety**: Validation prevents directory traversal
3. **Output Safety**: Results sanitized to remove sensitive path components
4. **Resource Limits**: Max results and timeout prevent resource exhaustion

---

## Acceptance Criteria

From feature spec User Story 1:

✓ Returns all matches with file paths, exact line numbers, and 2 lines of context
✓ Supports case-insensitive search
✓ Handles large result sets efficiently without memory exhaustion
✓ Respects exclusion patterns (node_modules, .git, etc.)
✓ Supports single file searches in addition to directory searches
