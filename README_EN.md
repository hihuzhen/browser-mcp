# Browser MCP Server

A browser MCP (Model Context Protocol) server implementation based on WebSocket communication, allowing AI assistants to control your browser. This project is developed with reference to [hangwin/mcp-chrome](https://github.com/hangwin/mcp-chrome), changing the communication between services to WebSocket and rewriting the app part in Python.

## 🚀 Project Features

- **WebSocket Communication**: Uses WebSocket instead of the original communication method, providing more efficient two-way communication
- **Python Backend**: App server completely rewritten in Python, leveraging the FastMCP framework
- **Browser Automation**: Allows AI assistants to perform various browser operations
- **Local Operation**: Runs completely locally, ensuring user privacy
- **Multiple Tool Support**: Supports screenshot, interactive operations, and other tools

## 📁 Project Structure

```
├── packages/           # Project packages
│   ├── app/            # Python implementation of MCP server
│   │   ├── src/mcp_server_browser/  # Main source code directory
│   │   ├── pyproject.toml  # Python project configuration
│   │   └── .gitignore      # Gitignore file for Python project
│   └── extension/      # Chrome browser extension
│       ├── common/     # Common code and constants
│       ├── entrypoints/ # Entry points (background and popup)
│       └── inject-scripts/ # Scripts injected into web pages
├── .gitignore          # Root directory gitignore file
└── LICENSE             # License file
```

### App Part (Python Implementation)

Main components:
- **WebSocket Server**: Implements WebSocket server, responsible for communicating with browser extension
- **MCP Service**: Implements MCP protocol, providing various browser control tools
- **Message Handling**: Processes WebSocket messages and MCP tool calls

### Extension Part (TypeScript Implementation)

Main components:
- **WebSocket Client**: Responsible for communicating with Python server
- **Tool Handler**: Processes tool call requests from the server
- **Inject Scripts**: Execute various operations in web pages

## 🛠️ Core Features

### Page Interaction
- **Element Click**: Click page elements via CSS selectors
- **Form Filling**: Fill forms or select options
- **Keyboard Operation**: Simulate keyboard input
- **Get Page Content**: Extract page text and HTML
- **Get Elements**: Get specific elements in the page
- **Interactive Element Recognition**: Automatically recognize interactive elements in the page

### Media and Network
- **Screenshot**: Capture the entire page or specific elements

## 🚀 Quick Start

### Prerequisites

- Python 3.9+ and pip/poetry/uv
- Chrome/Chromium browser

### Installation Steps

#### 1. Install Chrome Extension

```bash
cd extension
pnpm install
pnpm run build

# Or download a specific version from releases
```

Then in Chrome browser:
1. Open `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked"

#### 2. Run the Service

```json
{
  "mcpServers": {
    "browser-mcp-server": {
      "type": "stdio",
      "command": "uvx",
      "args": ["mcp-server-browser"]
    }
  }
}
```

#### 3. Connect Extension and Service

Click the extension icon in the browser to connect to the WebSocket service.

## 📝 Usage Instructions

### Using with MCP Protocol Clients

This service can be used with AI clients that support the MCP protocol, such as Claude, CherryStudio, etc.

## 🛠️ Available Tools List

Here are the main available tools:

### Browser Management
- `get_windows_and_tabs`: Get all open windows and tabs
- `browser_navigate`: Navigate to URL or refresh current tab
- `browser_close_tabs`: Close specific tabs or windows
- `browser_go_back_or_forward`: Browser history forward or backward

### Page Interaction
- `browser_click_element`: Click page elements
- `browser_fill_or_select`: Fill forms or select options
- `browser_get_elements`: Get page elements
- `browser_keyboard`: Simulate keyboard input
- `browser_get_web_content`: Get web page content
- `browser_screenshot`: Capture page screenshot

## 🔧 Development Guide

### Python Server Development

1. Ensure all dependencies are installed
2. You can configure WebSocket port and other parameters by modifying `app/src/mcp_server_browser/config.py`
3. You can specify the transport protocol when running: `python -m mcp_server_browser.app --transport stdio`

### Chrome Extension Development

1. Run `pnpm run build` to rebuild the extension after modifying the code
2. The extension will automatically reload (if in developer mode)
3. The default WebSocket connection address is `ws://localhost:18765`

## 📋 Notes

- This project is still under development and may have some bugs and imperfections
- Please ensure you understand the functions and potential risks of all tools before use
- Do not use this project for any illegal or unauthorized activities

## 🤝 Contribution

Contributions are welcome! Please submit issues and PRs to help improve this project.

## 📄 License

[MIT License](LICENSE)