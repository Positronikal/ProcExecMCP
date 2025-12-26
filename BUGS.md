# Bug Reports & Support

## Reporting Issues

If you encounter a bug or unexpected behavior, please report it via GitHub Issues:

1. Navigate to the [Issues](https://github.com/positronikal/procexec-mcp/issues) page
2. Click "New Issue"
3. Provide a clear title and detailed description
4. Include reproduction steps, expected behavior, and actual behavior
5. Add relevant logs, error messages, or screenshots

## Troubleshooting

### Common Issues

#### Tool Not Found Errors

**Problem:** `search_file_contents` fails with "ripgrep not found" error

**Solution:** 
- Ensure ripgrep is installed and in your system PATH
- Or set `PROCEXEC_RIPGREP_PATH` environment variable to the full path of the `rg` executable
- On Windows with Claude Desktop, PATH may be limited - use `PROCEXEC_RIPGREP_PATH`

**Example (Windows):**
```json
{
  "mcpServers": {
    "procexec": {
      "command": "uv",
      "args": ["--directory", "D:\\path\\to\\ProcExecMCP", "run", "procexec"],
      "env": {
        "PROCEXEC_RIPGREP_PATH": "C:\\Users\\YourName\\AppData\\Local\\Microsoft\\WinGet\\Packages\\BurntSushi.ripgrep.MSVC_Microsoft.Winget.Source_8wekyb3d8bbwe\\ripgrep-15.1.0-x86_64-pc-windows-msvc\\rg.exe"
      }
    }
  }
}
```

#### Command Timeout Errors

**Problem:** Commands timing out before completion

**Solution:**
- Increase timeout via `PROCEXEC_TIMEOUT` environment variable (milliseconds)
- Default is 30000ms (30 seconds)
- Valid range: 1000-300000ms (1 second to 5 minutes)

**Example:**
```json
"env": {
  "PROCEXEC_TIMEOUT": "60000"
}
```

#### Output Truncation

**Problem:** Command output is truncated with "[Output truncated...]" message

**Solution:**
- Increase output limit via `PROCEXEC_MAX_OUTPUT` environment variable (bytes)
- Default is 10485760 bytes (10MB)
- Valid range: 1024-104857600 bytes (1KB to 100MB)

**Example:**
```json
"env": {
  "PROCEXEC_MAX_OUTPUT": "20971520"
}
```

#### kill_process Not Working

**Problem:** `kill_process` tool returns "disabled" error

**Solution:**
- Process termination is disabled by default for safety
- Enable via `PROCEXEC_ENABLE_KILL` environment variable

**Example:**
```json
"env": {
  "PROCEXEC_ENABLE_KILL": "true"
}
```

**Security Note:** Only enable process termination if you trust the environment and understand the risks.

#### Permission Denied Errors

**Problem:** Operations fail with "Permission denied" errors

**Solution:**
- Check file/directory permissions
- Avoid running operations on system-protected paths
- On Windows, UAC may block certain operations
- Don't run Claude Desktop with elevated privileges unless necessary

#### Server Won't Start

**Problem:** MCP server fails to start or immediately crashes

**Solution:**
1. Verify Python 3.11+ is installed: `python --version`
2. Verify uv is installed: `uv --version`
3. Check server logs in Claude Desktop
4. Ensure working directory path is correct in config
5. Test server manually: `uv run procexec` in project directory

### Enable Detailed Logging

For debugging issues, you can enable detailed logging:

**Python Logging:**
```bash
# Run server with debug output
uv run python -m procexec --log-level DEBUG
```

**Check Claude Desktop Logs:**
- Windows: `%APPDATA%\Claude\logs\`
- macOS: `~/Library/Logs/Claude/`
- Linux: `~/.config/Claude/logs/`

### Performance Issues

#### Slow Search Operations

**Problem:** `search_file_contents` is slow on large codebases

**Solution:**
- Use more specific search paths (avoid searching entire drive)
- Use `exclude_patterns` to skip large directories (e.g., `node_modules`, `.git`)
- Use `file_types` filter to limit to specific file extensions
- Reduce `max_results` if you don't need all matches

#### Slow Process Listing

**Problem:** `list_processes` takes a long time to return

**Solution:**
- Use `name_filter` to limit results to specific process names
- Reduce `limit` parameter if you don't need all processes
- Note: On systems with 1000+ processes, some delay is normal

## Security Issues

**Do not report security vulnerabilities via GitHub Issues!**

For security issues, please follow the responsible disclosure process in [SECURITY.md](./SECURITY.md).

## Getting Help

- **Documentation:** See [README.md](./README.md) and [USING.md](./USING.md)
- **Security Architecture:** See [SECURITY_ARCHITECTURE.md](./SECURITY_ARCHITECTURE.md)
- **API Documentation:** See `docs/` directory (Doxygen generated)
- **Examples:** See `specs/001-procexec-mcp-server/quickstart.md`

## Known Issues

No known issues at this time. Check [GitHub Issues](https://github.com/positronikal/procexec-mcp/issues) for current bug reports.

## Version Information

When reporting issues, please include:
- ProcExecMCP version: Check `pyproject.toml` or `git describe --tags`
- Python version: `python --version`
- Operating system and version
- Claude Desktop version (if applicable)
- MCP Inspector results (if applicable)
