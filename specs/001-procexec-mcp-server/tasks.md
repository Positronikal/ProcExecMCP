# Implementation Tasks: ProcExecMCP Server

**Feature**: ProcExecMCP Server
**Branch**: `001-procexec-mcp-server`
**Created**: 2025-12-23
**Tech Stack**: Python 3.11+, FastMCP, psutil, Pydantic, uv
**Test Strategy**: Unit (mocked), Integration (safe commands), Security (attack scenarios)

---

## Implementation Strategy

**MVP Scope** (Recommended First Deliverable):
- Phase 1: Setup
- Phase 2: Foundational
- Phase 3: User Story 1 (P1) - search_file_contents tool

This MVP delivers immediate value for architectural code review by enabling pattern search across codebases.

**Incremental Delivery**:
1. **MVP** (US1): Search capability - enables code review and security audits
2. **V1.1** (US2): Command execution - enables running analysis tools
3. **V1.2** (US3): Process monitoring - enables system state awareness
4. **V1.3** (US4): Process termination - enables resource cleanup

Each user story is independently testable and delivers standalone value.

---

## Phase 1: Setup & Project Initialization

**Goal**: Initialize project structure, configure dependencies, and establish development environment.

### Tasks

- [X] T001 Initialize uv project with Python 3.11+ in repository root
- [X] T002 Create pyproject.toml with project metadata, dependencies (mcp, psutil, pydantic), and dev dependencies (pytest, pytest-cov)
- [X] T003 Create .gitignore for Python, uv, pytest, and IDE artifacts
- [X] T004 Create src/procexec/__init__.py with package version and exports
- [X] T005 Create src/procexec/tools/__init__.py for tool module exports
- [X] T006 Create src/procexec/utils/__init__.py for utility exports
- [X] T007 Create tests/__init__.py and subdirectories (unit/, integration/, security/)
- [X] T008 Create README.md with installation, configuration, and usage instructions (reference quickstart.md)
- [X] T009 Create docs/architecture.md documenting design decisions and patterns from research.md
- [X] T010 Create docs/security.md documenting security model, threat analysis, and mitigations

**Completion Criteria**:
- ✅ Project structure matches plan.md layout
- ✅ `uv sync` completes successfully
- ✅ All dependencies installed (<5 production packages)
- ✅ Documentation files created with initial content

---

## Phase 2: Foundational Infrastructure

**Goal**: Implement shared utilities and configuration that all user stories depend on.

**Blocking Dependencies**: Must complete before any user story implementation.

### Tasks

- [X] T011 [P] Implement ServerConfig class in src/procexec/server.py to load environment variables (PROCEXEC_TIMEOUT, PROCEXEC_MAX_OUTPUT, PROCEXEC_BLOCKED_PATHS, PROCEXEC_ENABLE_KILL) with validation
- [X] T012 [P] Implement validate_path() function in src/procexec/utils/validation.py with path resolution, traversal detection, and blocked path checks
- [X] T013 [P] Implement validate_directory() function in src/procexec/utils/validation.py using validate_path with directory check
- [X] T014 [P] Implement validate_file() function in src/procexec/utils/validation.py using validate_path with file check
- [X] T015 [P] Implement sanitize_path() function in src/procexec/utils/validation.py to remove sensitive path components from error messages
- [X] T016 [P] Implement sanitize_error_message() function in src/procexec/utils/validation.py to remove absolute paths, usernames, and IP addresses from error messages
- [X] T017 [P] Implement SanitizedError exception class in src/procexec/utils/validation.py with automatic message sanitization
- [X] T018 [P] Implement get_platform() function in src/procexec/utils/platform.py returning "windows" or "unix"
- [X] T019 [P] Implement is_windows() and is_unix() helper functions in src/procexec/utils/platform.py
- [X] T020 [P] Implement ErrorCategory enum in src/procexec/tools/schemas.py with values (validation, permission, not_found, timeout, security, system, unknown)
- [X] T021 [P] Implement ToolError Pydantic model in src/procexec/tools/schemas.py with category, message, and optional suggestion fields

**Completion Criteria**:
- ✅ All utility functions implemented and tested
- ✅ Configuration loading validates environment variables
- ✅ Path validation prevents traversal attacks
- ✅ Error sanitization removes sensitive information
- ✅ Platform detection works on Windows and Unix

**Unit Tests** (if TDD approach):
- [ ] T022 [P] Write tests/unit/test_validation.py with tests for validate_path, path traversal detection, blocked paths, and error sanitization
- [ ] T023 [P] Write tests/unit/test_platform.py with tests for platform detection on Windows and Unix (mocked)
- [ ] T024 [P] Write tests/unit/test_schemas.py with tests for ErrorCategory enum and ToolError model validation

**Security Tests**:
- [ ] T025 [P] Write tests/security/test_validation.py with path traversal attack scenarios (../../etc/passwd, ..\\..\\Windows\\System32\\config)
- [ ] T026 [P] Write tests/security/test_validation.py with sensitive path blocking tests

---

## Phase 3: User Story 1 (P1) - Content Search Across Codebase

**User Story**: Claude needs to search for code patterns, security vulnerabilities, TODO comments, or architectural concerns across the codebase.

**Independent Test**: Search for "TODO" pattern in test directory and verify all matches returned with file paths, line numbers, and 2 lines of context.

**Delivers Value**: Enables architectural code review and security audits.

### Input/Output Models

- [X] T027 [P] [US1] Implement SearchFileContentsInput Pydantic model in src/procexec/tools/schemas.py with pattern, path, case_sensitive, file_types, exclude_patterns, max_results, context_lines fields
- [X] T028 [P] [US1] Implement SearchMatch Pydantic model in src/procexec/tools/schemas.py with file_path, line_number, line_text, context_before, context_after fields
- [X] T029 [P] [US1] Implement SearchFileContentsOutput Pydantic model in src/procexec/tools/schemas.py with matches, total_matches, files_searched, truncated, search_time_ms fields

### Core Implementation

- [X] T030 [US1] Implement _check_ripgrep_available() helper function in src/procexec/tools/search.py to verify ripgrep binary exists in PATH
- [X] T031 [US1] Implement _build_ripgrep_args() helper function in src/procexec/tools/search.py to construct ripgrep arguments from SearchFileContentsInput (--json, --context, --line-number, --ignore-case, --type, --glob)
- [X] T032 [US1] Implement _parse_ripgrep_json() helper function in src/procexec/tools/search.py to parse ripgrep JSON output into SearchMatch objects
- [X] T033 [US1] Implement _execute_ripgrep() helper function in src/procexec/tools/search.py to run ripgrep via subprocess.run with timeout and error handling
- [X] T034 [US1] Implement search_file_contents_impl() function in src/procexec/tools/search.py orchestrating validation, ripgrep execution, and result parsing
- [X] T035 [US1] Decorate search_file_contents_impl() with @mcp.tool() in src/procexec/tools/search.py to expose as MCP tool with SearchFileContentsInput parameters and SearchFileContentsOutput return type

### Integration & Testing

- [X] T036 [US1] Write tests/integration/test_search_integration.py with real ripgrep tests: search for TODO in test files, case-insensitive search, file type filtering, exclusion patterns, context lines
- [ ] T037 [US1] Write tests/security/test_search_security.py with security tests: path traversal in search path, regex length limits, max_results enforcement, large result set handling

**Completion Criteria**:
- ✅ search_file_contents tool registered in FastMCP
- ✅ Ripgrep integration working on Windows and Unix
- ✅ All acceptance scenarios from spec.md pass
- ✅ Security tests validate input validation and resource limits
- ✅ Performance: <5s for 10,000-file codebase
- ✅ Independent test passes: search for "TODO" returns all matches with context

**Unit Tests** (if TDD approach):
- [ ] T038 [P] [US1] Write tests/unit/test_search.py with mocked subprocess tests for ripgrep argument construction, JSON parsing, error handling, and timeout enforcement

---

## Phase 4: User Story 2 (P1) - Command Execution for Analysis Tools

**User Story**: Claude needs to execute linters, static analysis tools, and build commands to validate code quality and assess project state.

**Independent Test**: Execute "python --version" and verify stdout contains "Python", stderr is empty, and exit code is 0.

**Delivers Value**: Enables running analysis tools for automated quality assessment.

### Input/Output Models

- [ ] T039 [P] [US2] Implement ExecuteCommandInput Pydantic model in src/procexec/tools/schemas.py with command, working_directory, timeout_ms, capture_output fields and @field_validator for empty command check
- [ ] T040 [P] [US2] Implement ExecuteCommandOutput Pydantic model in src/procexec/tools/schemas.py with stdout, stderr, exit_code, execution_time_ms, timed_out, output_truncated fields

### Core Implementation

- [ ] T041 [US2] Implement _parse_command_to_args() helper function in src/procexec/tools/execute.py using shlex.split with platform-specific posix parameter (Windows: posix=False, Unix: posix=True)
- [ ] T042 [US2] Implement _validate_working_directory() helper function in src/procexec/tools/execute.py using validate_directory from utils
- [ ] T043 [US2] Implement _enforce_output_limit() helper function in src/procexec/tools/execute.py to truncate output if exceeds configured max size
- [ ] T044 [US2] Implement _execute_subprocess() helper function in src/procexec/tools/execute.py calling subprocess.run with args list, shell=False, capture_output=True, timeout, cwd, and exception handling (TimeoutExpired, FileNotFoundError, PermissionError)
- [ ] T045 [US2] Implement execute_command_impl() function in src/procexec/tools/execute.py orchestrating command parsing, directory validation, subprocess execution, output limiting, and timing
- [ ] T046 [US2] Decorate execute_command_impl() with @mcp.tool() in src/procexec/tools/execute.py to expose as MCP tool with ExecuteCommandInput parameters and ExecuteCommandOutput return type

### Integration & Testing

- [ ] T047 [US2] Write tests/integration/test_execute_integration.py with safe command tests: echo/print commands, working directory changes, timeout enforcement with sleep commands, exit code handling
- [ ] T048 [US2] Write tests/security/test_injection.py with shell injection tests: semicolon attacks (; rm -rf /), pipe attacks (| cat /etc/passwd), command substitution ($(malicious), `malicious`), ampersand attacks (&& format C:)

**Completion Criteria**:
- ✅ execute_command tool registered in FastMCP
- ✅ Command parsing prevents shell injection (no shell=True)
- ✅ All acceptance scenarios from spec.md pass
- ✅ Security tests validate injection prevention
- ✅ Timeout enforcement accurate within 100ms
- ✅ Independent test passes: "python --version" executes successfully

**Unit Tests** (if TDD approach):
- [ ] T049 [P] [US2] Write tests/unit/test_execute.py with mocked subprocess tests for command parsing (shlex.split), timeout handling, output limiting, working directory validation, and error sanitization

---

## Phase 5: User Story 3 (P2) - Process Monitoring

**User Story**: Claude needs to check which processes are running to understand system state and identify resource usage issues.

**Independent Test**: List all processes, verify PID/name/CPU/memory/cmdline returned, then filter by "python" and verify only Python processes returned.

**Delivers Value**: Enables system state awareness and troubleshooting.

### Input/Output Models

- [ ] T050 [P] [US3] Implement ListProcessesInput Pydantic model in src/procexec/tools/schemas.py with name_filter, sort_by (enum: cpu, memory, pid, name), limit fields
- [ ] T051 [P] [US3] Implement ProcessInfo Pydantic model in src/procexec/tools/schemas.py with pid, name, cpu_percent, memory_mb, cmdline, status fields
- [ ] T052 [P] [US3] Implement ListProcessesOutput Pydantic model in src/procexec/tools/schemas.py with processes, total_count, truncated, retrieval_time_ms fields

### Core Implementation

- [ ] T053 [US3] Implement _get_process_info() helper function in src/procexec/tools/processes.py to safely get process info using psutil.Process with exception handling (NoSuchProcess, AccessDenied, ZombieProcess)
- [ ] T054 [US3] Implement _filter_processes() helper function in src/procexec/tools/processes.py to apply name filter (case-insensitive substring match)
- [ ] T055 [US3] Implement _sort_processes() helper function in src/procexec/tools/processes.py to sort by cpu, memory, pid, or name
- [ ] T056 [US3] Implement _limit_processes() helper function in src/procexec/tools/processes.py to apply result limit and set truncated flag
- [ ] T057 [US3] Implement list_processes_impl() function in src/procexec/tools/processes.py using psutil.process_iter to iterate all processes, filter, sort, limit, and return ListProcessesOutput
- [ ] T058 [US3] Decorate list_processes_impl() with @mcp.tool() in src/procexec/tools/processes.py to expose as MCP tool with ListProcessesInput parameters and ListProcessesOutput return type

### Integration & Testing

- [ ] T059 [US3] Write tests/integration/test_processes_integration.py with real psutil tests: list all processes, filter by name, sort by memory/cpu, limit results, verify all fields populated

**Completion Criteria**:
- ✅ list_processes tool registered in FastMCP
- ✅ psutil integration working on Windows and Unix
- ✅ All acceptance scenarios from spec.md pass
- ✅ Performance: <2s for process list retrieval
- ✅ Independent test passes: list all processes, filter by "python"

**Unit Tests** (if TDD approach):
- [ ] T060 [P] [US3] Write tests/unit/test_processes.py with mocked psutil tests for process iteration, filtering, sorting, limiting, and exception handling (NoSuchProcess, AccessDenied)

---

## Phase 6: User Story 4 (P3) - Process Termination

**User Story**: Claude needs to terminate stuck or hung processes to clean up system resources.

**Independent Test**: Start a test process (e.g., sleep), call kill_process with PID, verify process no longer exists and success=true returned.

**Delivers Value**: Enables system resource management and cleanup.

### Input/Output Models

- [ ] T061 [P] [US4] Implement KillProcessInput Pydantic model in src/procexec/tools/schemas.py with pid, force, timeout_seconds fields
- [ ] T062 [P] [US4] Implement KillProcessOutput Pydantic model in src/procexec/tools/schemas.py with success, pid, message, termination_time_ms, forced fields

### Core Implementation

- [ ] T063 [US4] Implement _validate_process_exists() helper function in src/procexec/tools/processes.py to check if PID exists using psutil.pid_exists
- [ ] T064 [US4] Implement _terminate_process() helper function in src/procexec/tools/processes.py to call proc.terminate() (SIGTERM/WM_CLOSE) and wait for termination with timeout
- [ ] T065 [US4] Implement _kill_process_forced() helper function in src/procexec/tools/processes.py to call proc.kill() (SIGKILL/TerminateProcess) for forced termination
- [ ] T066 [US4] Implement kill_process_impl() function in src/procexec/tools/processes.py orchestrating PID validation, graceful/forced termination, timing, and error handling (NoSuchProcess, AccessDenied, TimeoutExpired)
- [ ] T067 [US4] Decorate kill_process_impl() with @mcp.tool() in src/procexec/tools/processes.py to expose as MCP tool with KillProcessInput parameters and KillProcessOutput return type
- [ ] T068 [US4] Add PROCEXEC_ENABLE_KILL check in kill_process_impl() to allow disabling the tool via environment variable

### Integration & Testing

- [ ] T069 [US4] Write tests/integration/test_processes_integration.py with process termination tests: graceful termination, forced termination, non-existent PID error, permission denied error (if testable)

**Completion Criteria**:
- ✅ kill_process tool registered in FastMCP
- ✅ Process termination working on Windows and Unix
- ✅ All acceptance scenarios from spec.md pass
- ✅ Security: cannot be disabled by user, only via server config
- ✅ Independent test passes: terminate test process successfully

**Unit Tests** (if TDD approach):
- [ ] T070 [P] [US4] Write tests/unit/test_processes.py with mocked psutil tests for process termination, forced kill, PID validation, timeout handling, and exception handling

---

## Phase 7: Server Integration & Entry Point

**Goal**: Wire all tools into FastMCP server and create executable entry point.

**Dependencies**: All user stories (US1-US4) must be complete.

### Tasks

- [ ] T071 Import all tool functions in src/procexec/server.py (search_file_contents_impl, execute_command_impl, list_processes_impl, kill_process_impl)
- [ ] T072 Create FastMCP instance in src/procexec/server.py with name="ProcExecMCP", json_response=True, stateless_http=True
- [ ] T073 Load ServerConfig from environment in src/procexec/server.py and store as server state (accessible via Context)
- [ ] T074 Implement main() function in src/procexec/__main__.py to call mcp.run(transport="streamable-http") from server.py
- [ ] T075 Add __main__ block in src/procexec/__main__.py to call main() for python -m procexec execution
- [ ] T076 Add [project.scripts] entry in pyproject.toml mapping "procexec" command to "procexec.__main__:main"

**Completion Criteria**:
- ✅ All 4 tools registered and accessible
- ✅ Server starts successfully with `uv run procexec`
- ✅ Server responds to MCP protocol requests
- ✅ Configuration loaded from environment variables

---

## Phase 8: Testing & Quality Assurance

**Goal**: Achieve >80% code coverage and validate all security requirements.

**Dependencies**: Phase 7 complete.

### Security Testing

- [ ] T077 Run all security tests in tests/security/ and verify 100% pass rate: injection prevention, path traversal blocking, resource limit enforcement, error message sanitization
- [ ] T078 Perform manual security review: verify no shell=True, validate all timeout enforcement, check all input validation, review error messages for leaks
- [ ] T079 Test edge cases from spec.md: large result sets, malicious commands, system process termination attempts, concurrent requests

### Integration Testing

- [ ] T080 Test all user story independent tests end-to-end: US1 (TODO search), US2 (python --version), US3 (list python processes), US4 (terminate test process)
- [ ] T081 Test Claude Desktop integration: add server to claude_desktop_config.json, verify tools available, test each tool from Claude interface

### Coverage & CI

- [ ] T082 Run `uv run pytest --cov=src/procexec --cov-report=html --cov-report=term-missing` and verify >80% coverage
- [ ] T083 Review coverage report, add unit tests for any uncovered critical paths (especially error handlers and security validation)
- [ ] T084 Set up pytest configuration in pyproject.toml with coverage requirements and test discovery settings

**Completion Criteria**:
- ✅ All tests pass (unit, integration, security)
- ✅ Code coverage >80%
- ✅ All security requirements verified
- ✅ All acceptance scenarios pass
- ✅ Claude Desktop integration working

---

## Phase 9: Polish & Documentation

**Goal**: Complete documentation, polish error messages, and prepare for release.

**Dependencies**: Phase 8 complete.

### Documentation

- [ ] T085 [P] Complete README.md with full installation instructions, prerequisites (Python 3.11+, uv, ripgrep), Claude Desktop configuration, troubleshooting guide
- [ ] T086 [P] Complete docs/architecture.md with architecture decisions, design patterns, technology choices, and rationale
- [ ] T087 [P] Complete docs/security.md with threat model, attack vectors, mitigations, security best practices, and configuration recommendations
- [ ] T088 [P] Add inline code documentation (docstrings) to all public functions following Google style guide
- [ ] T089 [P] Create CHANGELOG.md documenting version 1.0.0 features and changes

### Polish

- [ ] T090 [P] Review all error messages for clarity and ensure they follow sanitization guidelines (no sensitive info leaks)
- [ ] T091 [P] Review all tool descriptions in @mcp.tool() decorators for clarity and helpfulness to Claude
- [ ] T092 [P] Add logging statements at key points (tool invocation, ripgrep execution, process operations) using Python logging module
- [ ] T093 [P] Test on both Windows and Unix systems, document any platform-specific behaviors or issues

### Release Preparation

- [ ] T094 Update pyproject.toml version to 1.0.0 and finalize metadata (description, authors, license, repository URL)
- [ ] T095 Create GitHub release with release notes, installation instructions, and quickstart guide
- [ ] T096 Verify all documentation is up-to-date and references correct paths and configuration values

**Completion Criteria**:
- ✅ All documentation complete and accurate
- ✅ Error messages clear and sanitized
- ✅ Cross-platform testing complete
- ✅ Ready for production use

---

## Task Dependencies & Parallel Execution

### Dependency Graph (Story Completion Order)

```
Phase 1 (Setup) → Phase 2 (Foundational) → [Phase 3 (US1) ∥ Phase 4 (US2) ∥ Phase 5 (US3) ∥ Phase 6 (US4)] → Phase 7 (Integration) → Phase 8 (Testing) → Phase 9 (Polish)
```

**Critical Path**: Phase 1 → Phase 2 → Phase 3 (US1) → Phase 7 (Integration) for MVP

**Parallel Opportunities**:
- **Phase 1** (Setup): Tasks T001-T010 can be parallelized (all [P] marked would be if independent)
- **Phase 2** (Foundational): All tasks T011-T021 are parallelizable ([P] marked)
- **User Stories**: Phase 3 (US1), Phase 4 (US2), Phase 5 (US3), Phase 6 (US4) are fully independent and can be implemented in parallel by different developers
- **Phase 9** (Polish): Documentation tasks T085-T089 are parallelizable ([P] marked)

### Parallel Execution Examples

**MVP Implementation (Phase 3 - US1)**:
```
Developer A: T027-T029 (Models) ∥ Developer B: T030-T033 (Helpers)
Then: T034 (Core) → T035 (Integration) → T036-T037 (Tests)
```

**Full Feature Development** (after Phase 2):
```
Team A: Phase 3 (US1) - search_file_contents
Team B: Phase 4 (US2) - execute_command
Team C: Phase 5 (US3) - list_processes
Team D: Phase 6 (US4) - kill_process
→ All converge at Phase 7 (Integration)
```

### MVP Delivery Path (Recommended)

**Sprint 1** (Estimated scope: Foundation + Search):
1. Phase 1: Setup (T001-T010)
2. Phase 2: Foundational (T011-T026)
3. Phase 3: User Story 1 (T027-T038)
4. Phase 7: Integration for US1 only (T071-T076, minimal)
5. Phase 8: Testing for US1 (T077-T081, subset)

**MVP Outcome**: Deployable server with search_file_contents tool enabling architectural code review.

**Sprint 2+**: Add US2, US3, US4 incrementally.

---

## Task Summary

**Total Tasks**: 96 tasks

**Task Breakdown by Phase**:
- Phase 1 (Setup): 10 tasks
- Phase 2 (Foundational): 16 tasks (11 implementation + 5 testing)
- Phase 3 (US1): 12 tasks (9 implementation + 3 testing)
- Phase 4 (US2): 11 tasks (8 implementation + 3 testing)
- Phase 5 (US3): 11 tasks (8 implementation + 3 testing)
- Phase 6 (US4): 10 tasks (8 implementation + 2 testing)
- Phase 7 (Integration): 6 tasks
- Phase 8 (Testing & QA): 8 tasks
- Phase 9 (Polish): 12 tasks

**Task Breakdown by User Story**:
- Setup/Infrastructure: 32 tasks
- US1 (P1 - Search): 12 tasks
- US2 (P1 - Execute): 11 tasks
- US3 (P2 - List): 11 tasks
- US4 (P3 - Kill): 10 tasks
- Integration/Testing/Polish: 20 tasks

**Parallelizable Tasks**: 45 tasks marked with [P]

**Independent Test Coverage**:
- ✅ US1: Search for "TODO" pattern in test directory
- ✅ US2: Execute "python --version" command
- ✅ US3: List processes, filter by "python"
- ✅ US4: Terminate test process by PID

---

## Implementation Notes

1. **Security is Non-Negotiable**: All security tests must pass before merge. No shell=True, all inputs validated, all error messages sanitized.

2. **Test as You Go**: Write unit tests for each function as you implement it (TDD approach optional but recommended for critical security code).

3. **Platform Testing**: Test on both Windows and Unix throughout development, not just at the end.

4. **ripgrep Dependency**: Verify ripgrep is installed before implementing search tool. Installation instructions in README.md.

5. **Configuration First**: Implement Phase 2 (Foundational) completely before starting any user stories. All user stories depend on these utilities.

6. **Independent Stories**: Each user story (US1-US4) can be developed and tested independently. They share only Phase 2 utilities.

7. **Error Handling**: Every function must handle errors gracefully and return sanitized error messages. Use SanitizedError class consistently.

8. **Timeout Enforcement**: All operations that could run indefinitely (ripgrep, subprocess, psutil operations) must have timeouts.

9. **Documentation**: Update docs/ as you implement, not at the end. Keep architecture.md and security.md current.

10. **MVP Focus**: Deliver US1 (search) first. It provides immediate value and validates the entire architecture (FastMCP, Pydantic, utilities).

---

## Format Validation

✅ All tasks follow strict checklist format:
- Checkbox (`- [ ]`)
- Task ID (T001-T096)
- [P] marker for parallelizable tasks
- [USn] label for user story tasks (US1-US4)
- Clear description with file paths

✅ User stories organized by priority (P1, P2, P3)

✅ Independent test criteria defined for each story

✅ Dependency graph and parallel execution plan provided

✅ MVP scope clearly identified (Phase 1-3, 7-8 subset)
