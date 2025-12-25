# ProcExecMCP Constitution

## Core Principles

### I. Unix Philosophy Adherence
Do one thing (stateless command execution and process management) and do it well. Exactly 4 tools, no feature creep. Each tool has a single, well-defined purpose. Tool interfaces are simple and composable. Token efficiency in all responses - no unnecessary verbosity.

### II. Security-First Design
All command execution validated and sanitized before execution. Mandatory timeouts on all operations (default 30s, configurable). Resource limits enforced: output size (10MB default), process operations rate-limited. No shell injection vulnerabilities - use subprocess argument lists only. Path traversal prevention for all file operations. Graceful degradation when permissions denied.

### III. Stateless Operation Model (NON-NEGOTIABLE)
No persistent sessions or interactive process connections. Each tool call is independent and self-contained. No state management between tool invocations. Command execution returns complete results in single response. Process management operates on existing PIDs only.

### IV. Code Quality Standards
Follow Positronikal Coding Standards: procedural, structured paradigm. Apply GNU Coding Standards principles. Clear, self-documenting code over clever abstractions. Comprehensive input validation and error handling on every tool. Type safety enforced using Pydantic schemas for all tool inputs.

### V. Testing Requirements
Unit tests for each tool function with mocked dependencies. Integration tests with safe command execution only. Security tests for validation and resource limits. Maintain >80% code coverage. All tests must pass before merge.

## Cross-Platform Requirements

Primary target: Windows 11 (development workstation environment)
Secondary target: Unix/Linux compatibility where practical
Platform-specific logic isolated in `utils/platform.py`
Transparent handling: Windows (PowerShell, Stop-Process) vs Unix (bash, kill)
Consistent tool interfaces regardless of underlying platform

## Documentation Standards

README.md: Installation, usage examples, configuration, security notes
Architecture decisions documented with rationale in `docs/architecture.md`
Security considerations explicitly documented in `docs/security.md`
API documentation includes Pydantic schemas and usage examples
Keep all documentation token-efficient and scannable

## Technology Constraints

- Python 3.11+ with uv for dependency management
- FastMCP framework for MCP protocol implementation
- psutil for cross-platform process management
- System ripgrep binary (no Python ripgrep dependency)
- Standard library preferred over third-party libraries when possible
- Total dependencies: <5 production packages

## Anti-Patterns (REJECTED)

- Interactive sessions or persistent process connections
- Feature additions beyond the 4 core tools
- Telemetry, A/B testing, or onboarding flows
- Complex state management or session tracking
- Security shortcuts or "good enough" validation
- Clever code that sacrifices clarity

## Success Criteria

All 4 tools implemented: `search_file_contents`, `execute_command`, `list_processes`, `kill_process`
Complete test coverage with passing unit, integration, and security tests
Security review passes all validation checks
Positronikal Coding Standards compliance verified
Seamless integration with Claude for Windows
Documentation complete and accurate
Can reliably execute analysis tools, search code, and manage processes

## Governance

This constitution supersedes all other development practices and guidelines. All implementation decisions must align with these principles. Security requirements are non-negotiable and cannot be compromised for convenience. Any amendments require architectural review and documentation update. Complexity must be justified against the Unix Philosophy principle of simplicity.

**Version**: 1.0.0 | **Ratified**: 2024-12-23 | **Last Amended**: 2024-12-23