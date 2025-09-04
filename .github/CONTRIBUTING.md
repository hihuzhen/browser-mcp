# Contributing to Browser MCP Server

First off, thank you for considering contributing to Browser MCP Server! It's people like you that make this project better.

## Table of Contents
- [Getting Started](#getting-started)
- [How Can I Contribute?](#how-can-i-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Pull Requests](#pull-requests)
- [Development Environment Setup](#development-environment-setup)
  - [Python Server](#python-server)
  - [Chrome Extension](#chrome-extension)
- [Coding Guidelines](#coding-guidelines)
- [Commit Message Guidelines](#commit-message-guidelines)

## Getting Started

Before you start contributing, please make sure you have:
- A GitHub account
- Git installed on your local machine
- Python 3.9+ for the server part
- Node.js and pnpm for the extension part
- Chrome/Chromium browser for testing

## How Can I Contribute?

### Reporting Bugs

If you find a bug, please [create an issue](https://github.com/[YOUR_USERNAME]/browser-mcp/issues/new?template=bug_report.md) using the bug report template. Be sure to include:
- A clear and descriptive title
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Environment information (OS, browser version, etc.)
- Screenshots if applicable

### Suggesting Enhancements

If you have an idea for an enhancement, please [create an issue](https://github.com/[YOUR_USERNAME]/browser-mcp/issues/new?template=feature_request.md) using the feature request template. Be sure to include:
- A clear and descriptive title
- A detailed description of the proposed feature
- How it would benefit the project
- Any alternative solutions you've considered

### Pull Requests

If you want to contribute code, follow these steps:

1. Fork the repository
2. Create a new branch for your feature or bug fix
3. Make your changes
4. Test your changes thoroughly
5. Commit your changes with a descriptive commit message
6. Push your branch to your fork
7. Create a pull request

When creating a pull request, please:
- Reference any related issues
- Provide a clear description of your changes
- Explain how you tested your changes
- Update documentation if necessary

## Development Environment Setup

### Python Server

1. Navigate to the `packages/app` directory
2. Install dependencies using `uv install` (or `pip install -e .` if using pip)
3. Run the server with `python -m mcp_server_browser.app`

### Chrome Extension

1. Navigate to the `packages/extension` directory
2. Install dependencies using `pnpm install`
3. Build the extension using `pnpm run build`
4. Load the unpacked extension in Chrome (see [README_EN.md](../README_EN.md#quick-start) for details)

## Coding Guidelines

- Follow the existing code style
- Write clear and concise comments
- Ensure your code is well-tested
- Keep functions and methods focused on a single task
- Use descriptive variable and function names

## Commit Message Guidelines

We recommend using the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification for your commit messages. This helps with automated versioning and changelog generation.

Examples:
- `fix: correct WebSocket connection handling`
- `feat: add new screenshot tool implementation`
- `docs: update installation instructions`
- `style: format code according to PEP 8`
- `refactor: reorganize tool handler structure`
- `test: add unit tests for browser navigation`
- `chore: update dependencies`

## Questions?

If you have any questions, feel free to reach out to the project maintainers or ask in the GitHub discussions.

Thank you for your contribution!