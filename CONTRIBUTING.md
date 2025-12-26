# Contributing

We welcome contributions to ProcExecMCP! Please follow these guidelines to ensure a smooth development process.

## How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes with comprehensive tests
4. Ensure all tests pass (`uv run pytest`)
5. Update documentation for any API changes
6. Submit a pull request

## Guidelines

- Follow the [Positronikal Coding Standards](https://github.com/positronikal/coding-standards)
- Add comprehensive tests for new features (maintain >80% coverage)
- Update relevant documentation files
- Ensure cross-platform compatibility (Windows & Unix)
- Follow security best practices (see [SECURITY_ARCHITECTURE.md](./SECURITY_ARCHITECTURE.md))

## GIT AND GITHUB

GitHub is the sole provider of public repositories and Git is the sole version control system (VCS) for this project. Contributing developers are required to use this service and method. Accounts belonging to contributing developers that do not use two-factor authentication are automatically rejected by GitHub. Pull requests that are not signed using GPG that authenticates the developer's identity are likely to be rejected.

## Coding Standards

This project follows the [Positronikal Coding Standards](https://github.com/positronikal/coding-standards), which emphasize:

- **Unix Philosophy:** Simple, focused, composable tools
- **GNU Coding Standards:** Clear, maintainable code structure
- **Procedural Programming:** Functional decomposition and clarity
- **Security-First Design:** No compromises on security

Key technical standards:
- **No `shell=True`** in subprocess calls (security requirement)
- **Input validation** via Pydantic schemas
- **Error sanitization** to prevent information leakage
- **Resource limits** (timeouts, output size, result counts)
- **Cross-platform compatibility** (Windows & Unix)

## Testing Requirements

All contributions must include:
- **Unit tests** with mocked dependencies
- **Integration tests** with real execution
- **Security tests** for any security-relevant code
- **Minimum 80% code coverage** for new code

Run tests:
```bash
# All tests
uv run pytest

# With coverage
uv run pytest --cov=src/procexec --cov-report=html

# Security tests only
uv run pytest tests/security/ -v
```

## Licensing

This project is licensed under the GNU General Public License (GPLv3), but it is not a GNU project and its copyright is not assigned to the Free Software Foundation (FSF). This means that while the project is free and open-source, the legal responsibility for defending the license rests with the project's maintainers.

By contributing to this project, you agree that your contributions will be licensed under the same license as the project (GPLv3).

For any non-trivial contribution, we require a signed contributor license agreement (CLA). This is a standard practice in many open-source projects and helps protect both you and the project. To get a copy of the CLA, please email [hoyt.harness@gmail.com](mailto:hoyt.harness@gmail.com).

## READ ALSO

- [Positronikal Coding Standards](https://positronikal.github.io/)
- [GNU Coding Standards](https://www.gnu.org/prep/standards/)
- [MCP Specification](https://spec.modelcontextprotocol.io/)
