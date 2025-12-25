# Implementation Plan: ProcExecMCP Server

**Branch**: `001-procexec-mcp-server` | **Date**: 2025-12-23 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-procexec-mcp-server/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build ProcExecMCP, a stateless command execution and process management MCP server that enables Claude (acting in an architectural role on Windows) to search code content, execute commands, monitor processes, and terminate processes. The server exposes 4 MCP tools using FastMCP with Python 3.11+, psutil for cross-platform process management, and system ripgrep for file content search. Security is paramount: no shell injection vulnerabilities, mandatory timeouts, resource limits, path validation, and sanitized error messages.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**:
- FastMCP (from mcp Python SDK) for MCP protocol implementation
- psutil for cross-platform process management
- System ripgrep binary (rg) invoked via subprocess for file content search
- Pydantic for input validation schemas
- uv for dependency management and packaging

**Storage**: N/A (stateless server)
**Testing**: pytest with unit tests (mocked subprocess), integration tests (safe commands only), security tests
**Target Platform**: Windows 11 primary, Unix/Linux secondary compatibility
**Project Type**: Single server application
**Performance Goals**:
- Search operations complete in <5s for 10,000-file codebases
- Process list retrieval in <2s
- Timeout enforcement accurate within 100ms

**Constraints**:
- No shell=True in subprocess calls (security requirement)
- Default timeout: 30s (configurable via PROCEXEC_TIMEOUT env var)
- Default output limit: 10MB (configurable via PROCEXEC_MAX_OUTPUT env var)
- Stateless operation model (no sessions or persistent state)
- Procedural programming style per Positronikal Coding Standards

**Scale/Scope**:
- 4 MCP tools: search_file_contents, execute_command, list_processes, kill_process
- <5 production dependencies
- Target >80% code coverage
- Zero security vulnerabilities

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Unix Philosophy Adherence ✓ PASS
- **Single Purpose**: Exactly 4 tools with well-defined, non-overlapping purposes
- **Do One Thing Well**: Stateless command execution and process management only
- **Composability**: Tool interfaces are simple, accept clear inputs, return structured outputs
- **Token Efficiency**: All tool outputs are concise and structured

### II. Security-First Design ✓ PASS
- **Validation**: All inputs validated via Pydantic schemas before execution
- **No Shell Injection**: subprocess called with argument lists only (no shell=True)
- **Mandatory Timeouts**: Default 30s timeout on all operations, enforced via subprocess timeout parameter
- **Resource Limits**: Output size limit (10MB default), enforced during streaming
- **Path Traversal Prevention**: Path validation in utils/validation.py for all file operations
- **Graceful Degradation**: Permission errors handled without crashes

### III. Stateless Operation Model ✓ PASS
- **No Sessions**: Each tool call is completely independent
- **No State Management**: No persistent state between invocations
- **Self-Contained**: Each tool returns complete results in single response
- **Process Management**: Operates on existing PIDs only, no process creation or tracking

### IV. Code Quality Standards ✓ PASS
- **Positronikal Coding Standards**: Procedural, structured paradigm enforced
- **Clear Code**: Self-documenting function and variable names
- **Input Validation**: Comprehensive validation on every tool using Pydantic schemas
- **Error Handling**: All error paths handled gracefully
- **Type Safety**: Pydantic schemas enforce type safety for all tool inputs

### V. Testing Requirements ✓ PASS
- **Unit Tests**: Each tool function tested with mocked dependencies
- **Integration Tests**: Safe command execution only (echo, dir, ls)
- **Security Tests**: Validation and resource limit enforcement tested
- **Coverage**: Target >80% code coverage
- **CI**: All tests must pass before merge

### Cross-Platform Requirements ✓ PASS
- **Primary Target**: Windows 11 development workstation
- **Secondary Target**: Unix/Linux compatibility
- **Platform Abstraction**: utils/platform.py isolates platform-specific logic
- **Transparent Handling**: Consistent tool interfaces regardless of platform

### Technology Constraints ✓ PASS
- **Python 3.11+**: ✓
- **uv for dependency management**: ✓
- **FastMCP framework**: ✓
- **psutil for process management**: ✓
- **System ripgrep binary**: ✓
- **Standard library preferred**: ✓
- **Total dependencies**: <5 production packages ✓

**GATE STATUS**: ✓ ALL GATES PASS - Proceed to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
ProcExecMCP/
├── src/
│   └── procexec/
│       ├── __init__.py           # Package initialization
│       ├── __main__.py           # MCP server entry point (python -m procexec)
│       ├── server.py             # FastMCP server setup and configuration
│       ├── tools/
│       │   ├── __init__.py       # Tool package exports
│       │   ├── schemas.py        # Pydantic input validation schemas
│       │   ├── search.py         # search_file_contents tool implementation
│       │   ├── execute.py        # execute_command tool implementation
│       │   └── processes.py      # list_processes, kill_process tool implementations
│       └── utils/
│           ├── __init__.py       # Utility package exports
│           ├── validation.py     # Input validation helpers (path validation, etc.)
│           └── platform.py       # Cross-platform abstraction (Windows vs Unix)
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── test_search.py        # Unit tests for search tool (mocked subprocess)
│   │   ├── test_execute.py       # Unit tests for execute tool (mocked subprocess)
│   │   ├── test_processes.py     # Unit tests for process tools (mocked psutil)
│   │   ├── test_validation.py    # Unit tests for validation utilities
│   │   └── test_platform.py      # Unit tests for platform utilities
│   ├── integration/
│   │   ├── test_search_integration.py      # Integration tests with real ripgrep
│   │   ├── test_execute_integration.py     # Integration tests with safe commands
│   │   └── test_processes_integration.py   # Integration tests with real processes
│   └── security/
│       ├── test_injection.py     # Security tests for injection prevention
│       ├── test_limits.py        # Security tests for resource limits
│       └── test_validation.py    # Security tests for input validation
├── docs/
│   ├── architecture.md           # Architecture decisions and rationale
│   └── security.md               # Security considerations and threat model
├── pyproject.toml                # uv configuration, dependencies, metadata
├── README.md                     # Installation, usage, configuration
└── .gitignore                    # Python, uv, IDE artifacts
```

**Structure Decision**: Single project structure. This is a standalone MCP server with no frontend, backend split, or mobile components. The procedural programming style is reflected in the flat module structure with clear separation of concerns: tools (core functionality), utils (cross-cutting concerns), and tests (verification).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

N/A - No constitution violations. All complexity is justified by requirements and security constraints.

---

## Post-Design Constitution Re-Check

*Re-evaluation after Phase 1 design artifacts (data-model.md, contracts/, quickstart.md)*

### Design Validation Against Constitution

✅ **Unix Philosophy** - CONFIRMED
- Exactly 4 tools, each with single purpose
- No feature creep detected in design
- Tool interfaces remain simple and composable
- Data models are minimal and focused

✅ **Security-First Design** - CONFIRMED
- All 4 tools have comprehensive Pydantic input validation
- No shell=True confirmed in design patterns
- Timeout enforcement designed into execute_command (subprocess.run timeout parameter)
- Output size limits designed into execute_command and search_file_contents
- Path validation utilities designed (validate_path, validate_directory, validate_file)
- Error sanitization designed (sanitize_error_message, SanitizedError class)

✅ **Stateless Operation** - CONFIRMED
- Data model contains only request/response schemas, no persistent entities
- No session management in tool contracts
- Each tool designed to return complete results in single response
- Process management operates on PIDs only (no process tracking)

✅ **Code Quality Standards** - CONFIRMED
- Procedural design: tools in separate modules, utilities in utils/
- Type safety enforced via Pydantic schemas for all inputs/outputs
- Clear module structure: tools/, utils/, tests/
- Comprehensive error handling in contracts

✅ **Testing Requirements** - CONFIRMED
- Three-tier testing strategy designed: unit (mocked), integration (safe), security (attacks)
- Coverage target >80% specified
- All security attack vectors identified for testing

✅ **Cross-Platform Requirements** - CONFIRMED
- Platform abstraction layer designed (utils/platform.py)
- Contracts specify platform-agnostic interfaces
- Research identifies platform-specific handling (shlex.split posix parameter, psutil abstraction)

✅ **Technology Constraints** - CONFIRMED
- Python 3.11+ throughout design
- FastMCP framework usage confirmed
- psutil for process management designed
- System ripgrep via subprocess designed
- Total dependencies: mcp, psutil, pydantic (<5 ✓)

### Design Improvements Since Initial Check

1. **Enhanced Security**:
   - Added comprehensive path validation utilities
   - Designed error message sanitization
   - Specified regex length limits to prevent ReDoS

2. **Better Error Handling**:
   - Standardized ToolError model with categories
   - Sanitized messages that preserve utility

3. **Comprehensive Testing**:
   - Security test suite explicitly designed
   - Integration tests with safe commands only

**FINAL VERDICT**: ✅ ALL CONSTITUTION REQUIREMENTS MET - Design is ready for implementation (Phase 2: tasks.md generation)
