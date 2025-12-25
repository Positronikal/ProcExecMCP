# Quickstart Guide: ProcExecMCP

Get ProcExecMCP running in 5 minutes for architectural code review workflows with Claude for Windows.

---

## Prerequisites

- **Windows 11** (primary target) or **Unix/Linux** (secondary)
- **Python 3.11+** installed
- **uv** package manager ([installation guide](https://docs.astral.sh/uv/))
- **ripgrep (rg)** binary for file search ([installation guide](https://github.com/BurntSushi/ripgrep#installation))
- **Claude for Windows** (or Claude Desktop) installed

---

## Installation

### Step 1: Clone or Download

```bash
cd D:\dev\ARTIFICIAL_INTELLIGENCE\MCP
git clone <repository-url> ProcExecMCP
cd ProcExecMCP
```

### Step 2: Install Dependencies with uv

```bash
# Initialize uv project and install dependencies
uv sync
```

This installs:
- `mcp` (FastMCP framework)
- `psutil` (process management)
- `pydantic` (input validation)
- Development dependencies: `pytest`, `pytest-cov`

### Step 3: Verify ripgrep Installation

```bash
# Check if ripgrep is available
rg --version
```

If not installed:
- **Windows**: `winget install BurntSushi.ripgrep.MSVC`
- **macOS**: `brew install ripgrep`
- **Ubuntu/Debian**: `sudo apt install ripgrep`

---

## Configuration

### Step 4: Configure Claude for Windows

Edit `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "procexec": {
      "command": "uv",
      "args": [
        "--directory",
        "D:\\dev\\ARTIFICIAL_INTELLIGENCE\\MCP\\ProcExecMCP",
        "run",
        "procexec"
      ],
      "env": {
        "PROCEXEC_TIMEOUT": "30000",
        "PROCEXEC_MAX_OUTPUT": "10485760",
        "PROCEXEC_BLOCKED_PATHS": "C:\\Windows\\System32\\config,C:\\Windows\\System32\\drivers"
      }
    }
  }
}
```

**Configuration Options**:
- `PROCEXEC_TIMEOUT`: Command timeout in milliseconds (default: 30000)
- `PROCEXEC_MAX_OUTPUT`: Maximum output size in bytes (default: 10485760 = 10MB)
- `PROCEXEC_BLOCKED_PATHS`: Comma-separated list of paths to block (optional)
- `PROCEXEC_ENABLE_KILL`: Enable process termination (default: "true")

### Step 5: Restart Claude for Windows

Close and reopen Claude for Windows to load the new MCP server configuration.

---

## Verification

### Step 6: Test the Server

In Claude for Windows, try these commands:

```
Search for TODO comments in my project
```

```
Run 'python --version' command
```

```
List all running Python processes
```

### Step 7: Verify Tools are Available

Ask Claude:
```
What MCP tools do you have available?
```

You should see:
- ✅ `search_file_contents`
- ✅ `execute_command`
- ✅ `list_processes`
- ✅ `kill_process`

---

## Quick Usage Examples

### Example 1: Architectural Code Review

```
Use search_file_contents to find all TODO and FIXME comments in my Python project at D:\projects\myapp. Exclude test files and venv.
```

Claude will use:
```json
{
  "pattern": "TODO|FIXME",
  "path": "D:\\projects\\myapp",
  "case_sensitive": false,
  "file_types": ["py"],
  "exclude_patterns": ["test_*.py", "venv"],
  "context_lines": 2
}
```

### Example 2: Run Static Analysis

```
Execute 'pylint src/' in D:\projects\myapp and show me the results.
```

Claude will use:
```json
{
  "command": "pylint src/",
  "working_directory": "D:\\projects\\myapp",
  "timeout_ms": 60000
}
```

### Example 3: Check Running Processes

```
List all Node.js processes currently running, sorted by memory usage.
```

Claude will use:
```json
{
  "name_filter": "node",
  "sort_by": "memory",
  "limit": 50
}
```

### Example 4: Clean Up Stuck Process

```
Terminate process 1234 gracefully.
```

Claude will use:
```json
{
  "pid": 1234,
  "force": false,
  "timeout_seconds": 5
}
```

---

## Development Mode

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/procexec --cov-report=html

# Run specific test categories
uv run pytest tests/unit/          # Unit tests only
uv run pytest tests/integration/   # Integration tests only
uv run pytest tests/security/      # Security tests only
```

### Running Server Directly (Debugging)

```bash
# Run with stdio transport for MCP Inspector
uv run procexec

# Run with HTTP transport for browser testing
uv run python -m procexec --transport http
```

### Using MCP Inspector

```bash
# Terminal 1: Start server
uv run procexec

# Terminal 2: Start inspector
npx @modelcontextprotocol/inspector
```

Then connect to `http://localhost:8000/mcp` in the inspector.

---

## Troubleshooting

### Issue: "ripgrep not found"

**Solution**: Install ripgrep and ensure it's in PATH:
```bash
rg --version
```

### Issue: "Permission denied" errors

**Solution**:
1. Run Claude for Windows as administrator (if accessing system processes)
2. Or adjust `PROCEXEC_BLOCKED_PATHS` to allow specific paths

### Issue: "Timeout exceeded" for commands

**Solution**: Increase timeout in configuration:
```json
"env": {
  "PROCEXEC_TIMEOUT": "60000"
}
```

### Issue: Server not appearing in Claude

**Solution**:
1. Check `claude_desktop_config.json` syntax (valid JSON)
2. Verify paths are correct (use absolute paths)
3. Restart Claude for Windows
4. Check Claude logs: `%APPDATA%\Claude\logs`

### Issue: "Module not found" errors

**Solution**: Ensure dependencies are installed:
```bash
uv sync
```

---

## Next Steps

- Review [contracts/](./contracts/) for detailed tool specifications
- Read [data-model.md](./data-model.md) for input/output schemas
- Consult [research.md](./research.md) for implementation patterns
- Check [plan.md](./plan.md) for architecture decisions

---

## Security Best Practices

1. **Limit Blocked Paths**: Configure `PROCEXEC_BLOCKED_PATHS` to protect sensitive directories
2. **Set Reasonable Timeouts**: Prevent runaway commands with appropriate timeouts
3. **Review Command History**: Periodically review what commands Claude executes
4. **Disable Process Kill**: If not needed, set `PROCEXEC_ENABLE_KILL=false`
5. **Run as Non-Admin**: Unless necessary, run Claude without elevated privileges

---

## Common Workflows

### Workflow 1: Security Audit

1. Search for SQL injection patterns:
   ```
   Find potential SQL injection vulnerabilities in my Python code
   ```

2. Search for hardcoded credentials:
   ```
   Search for hardcoded passwords or API keys in my project
   ```

3. Check for unsafe function usage:
   ```
   Find all uses of eval() or exec() in Python files
   ```

### Workflow 2: Code Quality Review

1. Find all TODOs:
   ```
   List all TODO and FIXME comments in the codebase
   ```

2. Run linters:
   ```
   Run eslint on the frontend code and show results
   ```

3. Check test coverage:
   ```
   Execute pytest with coverage and analyze results
   ```

### Workflow 3: Performance Investigation

1. List resource-intensive processes:
   ```
   Show me the top 10 processes by CPU usage
   ```

2. Check for memory leaks:
   ```
   Monitor Python processes and their memory usage
   ```

3. Terminate stuck builds:
   ```
   Find and terminate any stuck npm processes
   ```

---

## Support

- **GitHub Issues**: [Report bugs or request features](repository-url/issues)
- **Documentation**: [Full documentation](./README.md)
- **Security**: [Report security issues](./SECURITY.md)
