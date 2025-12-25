# MCP Tool Contracts

This directory contains the contract definitions for all MCP tools exposed by ProcExecMCP server.

## Tool List

1. **search_file_contents** - Search for patterns in file contents across directories
2. **execute_command** - Execute commands safely with timeout and output limits
3. **list_processes** - List running processes with filtering and sorting
4. **kill_process** - Terminate processes by PID with optional forced termination

## Contract Format

Each tool contract specifies:
- Tool name and description
- Input schema (parameters with types and validation)
- Output schema (structured response format)
- Error conditions and messages
- Usage examples

These contracts follow the MCP specification and are implemented using FastMCP framework.
