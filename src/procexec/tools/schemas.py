"""Pydantic schemas for tool input/output validation and error handling."""

from enum import Enum
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ErrorCategory(str, Enum):
    """Error categories for tool execution failures."""

    VALIDATION = "validation"
    PERMISSION = "permission"
    NOT_FOUND = "not_found"
    TIMEOUT = "timeout"
    SECURITY = "security"
    SYSTEM = "system"
    UNKNOWN = "unknown"


class ToolError(BaseModel):
    """Standardized error response for tool failures.

    Attributes:
        category: Error category for programmatic handling
        message: Sanitized, human-readable error message
        suggestion: Optional suggestion for resolving the error
    """

    category: ErrorCategory = Field(
        description="Error category for programmatic handling"
    )

    message: str = Field(
        description="Sanitized, human-readable error message"
    )

    suggestion: str | None = Field(
        default=None,
        description="Optional suggestion for how to resolve the error"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "category": "timeout",
                    "message": "Command exceeded timeout limit of 30 seconds",
                    "suggestion": "Try increasing the timeout_ms parameter or optimizing the command"
                }
            ]
        }
    )


# Input/Output schemas for User Story 1 (search_file_contents)

class SearchFileContentsInput(BaseModel):
    """Input schema for search_file_contents tool."""

    pattern: str = Field(
        description="Regular expression pattern to search for",
        min_length=1,
        max_length=1000,
        examples=["TODO", r"def\s+\w+", r"import\s+\w+"]
    )

    path: str = Field(
        description="File or directory path to search in",
        examples=["C:\\projects\\myapp", "/home/user/code", "./src"]
    )

    case_sensitive: bool = Field(
        default=True,
        description="Whether the search should be case-sensitive"
    )

    file_types: list[str] | None = Field(
        default=None,
        description="File type filters (e.g., ['py', 'js', 'ts']). If None, search all files.",
        examples=[["py", "pyi"], ["js", "ts", "tsx"]]
    )

    exclude_patterns: list[str] | None = Field(
        default=None,
        description="Glob patterns to exclude (e.g., ['*.min.js', 'node_modules'])",
        examples=[["node_modules", "*.min.js"], ["venv", "__pycache__"]]
    )

    max_results: int = Field(
        default=1000,
        description="Maximum number of match results to return",
        ge=1,
        le=10000
    )

    context_lines: int = Field(
        default=2,
        description="Number of lines to include before and after each match",
        ge=0,
        le=10
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "pattern": "TODO",
                    "path": "./src",
                    "case_sensitive": False,
                    "file_types": ["py"],
                    "exclude_patterns": ["test_*.py", "venv"],
                    "max_results": 100,
                    "context_lines": 2
                }
            ]
        }
    )


class SearchMatch(BaseModel):
    """Single search match result."""

    file_path: str = Field(
        description="Absolute path to file containing the match"
    )

    line_number: int = Field(
        description="Line number of the match (1-indexed)",
        ge=1
    )

    line_text: str = Field(
        description="Content of the matched line"
    )

    context_before: list[str] = Field(
        description="Lines before the match (for context)",
        default_factory=list
    )

    context_after: list[str] = Field(
        description="Lines after the match (for context)",
        default_factory=list
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
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
            ]
        }
)

class SearchFileContentsOutput(BaseModel):
    """Output schema for search_file_contents tool."""

    matches: list[SearchMatch] = Field(
        description="List of search matches found"
    )

    total_matches: int = Field(
        description="Total number of matches found (may exceed returned matches if limited)",
        ge=0
    )

    files_searched: int = Field(
        description="Number of files searched",
        ge=0
    )

    truncated: bool = Field(
        description="Whether results were truncated due to max_results limit"
    )

    search_time_ms: int = Field(
        description="Time taken to complete search in milliseconds",
        ge=0
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "matches": [
                        {
                            "file_path": "/project/src/main.py",
                            "line_number": 42,
                            "line_text": "# TODO: Fix this",
                            "context_before": [],
                            "context_after": []
                        }
                    ],
                    "total_matches": 1,
                    "files_searched": 15,
                    "truncated": False,
                    "search_time_ms": 234
                }
            ]
        }
    )
