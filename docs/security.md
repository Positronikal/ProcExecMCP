# Security: ProcExecMCP

**Last Updated**: 2025-12-23
**Full Security Design**: See [research.md](../specs/001-procexec-mcp-server/research.md) Section 2 and 5

## Overview

Security is paramount in ProcExecMCP. The server prevents shell injection, path traversal, resource exhaustion, and information leakage through multiple defense layers.

## Threat Model

### Attack Vectors

1. **Shell Injection**: Malicious commands in execute_command
2. **Path Traversal**: `../../etc/passwd` in search paths
3. **Resource Exhaustion**: Large outputs, runaway commands, infinite loops
4. **Information Leakage**: Sensitive paths, usernames, system details in errors
5. **Denial of Service**: Timeout bypass, concurrent request flooding

### Trust Boundary

- **Trusted**: Claude (authenticated MCP client)
- **Untrusted**: User-provided patterns, paths, commands, PIDs

All inputs from the trust boundary are validated before execution.

## Security Measures

### 1. Shell Injection Prevention

**Threat**: Malicious command injection via execute_command

**Mitigation**:
- ❌ **NEVER** use `shell=True` in subprocess calls
- ✅ Parse commands with `shlex.split()` into argument lists
- ✅ Pass argument list directly to subprocess.run()
- ✅ Platform-specific parsing (posix parameter for Windows vs Unix)

**Example**:
```python
# INSECURE (never do this)
subprocess.run(command, shell=True)  # ❌ Shell injection vulnerable

# SECURE (implemented)
import shlex
args = shlex.split(command, posix=not is_windows())
subprocess.run(args, shell=False, timeout=timeout)  # ✅ Safe
```

**Test Coverage**: `tests/security/test_injection.py`

### 2. Path Traversal Prevention

**Threat**: Access to sensitive files via `../../etc/passwd` patterns

**Mitigation**:
- ✅ Resolve all paths to absolute form with `Path.resolve()`
- ✅ Detect `..` components after resolution
- ✅ Block access to sensitive system paths (configurable)
- ✅ Validate paths exist before operations

**Blocked Paths** (default):
- Windows: `C:\Windows\System32\config`, `C:\Windows\System32\drivers`
- Unix: `/etc/shadow`, `/etc/passwd`
- Configurable via `PROCEXEC_BLOCKED_PATHS`

**Example**:
```python
def validate_path(path_str: str) -> Path:
    path = Path(path_str).resolve()

    # Check for traversal
    if ".." in path.parts:
        raise ValueError("Path traversal not allowed")

    # Check blocked paths
    for blocked in BLOCKED_PATHS:
        if str(path).lower().startswith(blocked.lower()):
            raise ValueError("Access to sensitive path not allowed")

    return path
```

**Test Coverage**: `tests/security/test_validation.py`

### 3. Resource Limit Enforcement

**Threat**: Memory exhaustion, infinite loops, resource monopolization

**Mitigation**:
- ✅ **Timeouts**: Default 30s, configurable via `PROCEXEC_TIMEOUT`
- ✅ **Output Limits**: Default 10MB, configurable via `PROCEXEC_MAX_OUTPUT`
- ✅ **Result Limits**: Max 10,000 search results per query
- ✅ **Regex Limits**: Pattern max 1,000 chars (prevents ReDoS)

**Configuration**:
```json
{
  "env": {
    "PROCEXEC_TIMEOUT": "30000",          // 30 seconds
    "PROCEXEC_MAX_OUTPUT": "10485760",    // 10MB
    "PROCEXEC_RIPGREP_PATH": "C:\\tools\\ripgrep\\rg.exe"  // Optional: Custom ripgrep path
  }
}
```

**Test Coverage**: `tests/security/test_limits.py`

### 4. Error Message Sanitization

**Threat**: System information leakage via error messages

**Mitigation**:
- ✅ Remove absolute paths from error messages
- ✅ Replace paths with basenames or `[path]` placeholder
- ✅ Redact usernames and home directories
- ✅ Remove IP addresses and hostnames
- ✅ Generic error categories instead of specific system errors

**Example**:
```python
def sanitize_error_message(message: str) -> str:
    # Remove absolute paths
    message = re.sub(r'[A-Z]:\\[^\s]+', '[path]', message)
    message = re.sub(r'/(?:home|root|Users)/[^\s]+', '[path]', message)

    # Remove usernames
    message = re.sub(r'user\s+[\w]+', 'user [redacted]', message)

    # Remove IP addresses
    message = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '[IP]', message)

    return message
```

**Test Coverage**: `tests/unit/test_validation.py`

### 5. Input Validation

**Threat**: Invalid, malicious, or malformed inputs

**Mitigation**:
- ✅ Pydantic schema validation on all tool inputs
- ✅ Type checking, range validation, format validation
- ✅ Field-level validators for complex constraints
- ✅ Fail-fast on validation errors

**Example**:
```python
class SearchFileContentsInput(BaseModel):
    pattern: str = Field(min_length=1, max_length=1000)
    path: str
    max_results: int = Field(ge=1, le=10000)

    @field_validator('path')
    @classmethod
    def validate_path_exists(cls, v: str) -> str:
        # Custom validation logic
        return v
```

## Security Testing

### Attack Scenarios Tested

1. **Shell Injection**:
   - `; rm -rf /`
   - `| cat /etc/passwd`
   - `&& format C:`
   - `$(malicious command)`
   - `` `malicious command` ``

2. **Path Traversal**:
   - `../../etc/passwd`
   - `..\\..\\Windows\\System32\\config`
   - Symlink-based attacks

3. **Resource Exhaustion**:
   - Commands with infinite output
   - Regex catastrophic backtracking
   - Concurrent request flooding

4. **Information Leakage**:
   - Error messages revealing paths
   - Stack traces with system details

### Running Security Tests

```bash
uv run pytest tests/security/ -v
```

All security tests must pass before deployment.

## Configuration Best Practices

1. **Limit Timeouts**: Set reasonable timeouts (30-60s)
2. **Block Sensitive Paths**: Configure `PROCEXEC_BLOCKED_PATHS` appropriately
3. **Configure Ripgrep Path**: Use `PROCEXEC_RIPGREP_PATH` if ripgrep is not in PATH (common on Windows with Claude Desktop)
4. **Monitor Logs**: Review logs for suspicious patterns
5. **Disable Features**: Use `PROCEXEC_ENABLE_KILL=false` if process termination not needed
6. **Run Least Privilege**: Don't run Claude with admin privileges unless necessary

## Incident Response

If a security vulnerability is discovered:

1. **Do Not** open public GitHub issue
2. Contact maintainers privately
3. Provide detailed reproduction steps
4. Allow time for patch development
5. Coordinate disclosure timeline

## Security Checklist

Before deploying:
- [ ] All security tests passing
- [ ] No `shell=True` in codebase
- [ ] Path validation on all file operations
- [ ] Timeouts enforced on all operations
- [ ] Error messages sanitized
- [ ] Configuration reviewed for environment

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python subprocess security](https://docs.python.org/3/library/subprocess.html#security-considerations)
- [Path Traversal Prevention](https://owasp.org/www-community/attacks/Path_Traversal)
