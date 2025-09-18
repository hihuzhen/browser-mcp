# Browser MCP Server 🚀

[English](README_EN.md) | 简体中文

[![license](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE) [![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/downloads/) [![Stars](https://img.shields.io/github/stars/hihuzhen/browser-mcp.svg?style=social&label=Stars)](https://github.com/hihuzhen/browser-mcp/stargazers) [![Forks](https://img.shields.io/github/forks/hihuzhen/browser-mcp.svg?style=social&label=Forks)](https://github.com/hihuzhen/browser-mcp/network/members) [![PRs](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/hihuzhen/browser-mcp/pulls)

Browser MCP Server是一个基于WebSocket通信的浏览器MCP（Model Context Protocol）服务器实现，允许AI助手控制你的浏览器。

## 🚀 项目特点

- **WebSocket通信**: 使用WebSocket替代原有的通信方式，提供更高效的双向通信
- **Python后端**: App服务端完全使用Python重写，利用FastMCP框架
- **浏览器自动化**: 允许AI助手执行各种浏览器操作
- **本地运行**: 完全在本地运行，保证用户隐私
- **多工具支持**: 支持截图、交互式操作等多种工具

## 📁 项目结构

```
├── packages/           # 项目包
│   ├── app/            # Python实现的MCP服务器
│   │   ├── src/nep_browser_engine/  # 主源码目录
│   │   ├── pyproject.toml  # Python项目配置
│   │   └── .gitignore      # Python项目的gitignore文件
│   └── extension/      # Chrome浏览器扩展
│       ├── common/     # 通用代码和常量
│       ├── entrypoints/ # 入口点(background和popup)
│       └── inject-scripts/ # 注入到网页的脚本
├── .gitignore          # 根目录gitignore文件
└── LICENSE             # 许可证文件
```

### App部分（Python实现）

主要组件：
- **WebSocket服务**: 实现WebSocket服务器，负责与浏览器扩展通信
- **MCP服务**: 实现MCP协议，提供各种浏览器控制工具
- **消息处理**: 处理WebSocket消息和MCP工具调用

### Extension部分（TypeScript实现）

主要组件：
- **WebSocket客户端**: 负责与Python服务端通信
- **工具处理器**: 处理来自服务端的工具调用请求
- **注入脚本**: 在网页中执行各种操作

## 🛠️ 核心功能

### 页面交互
- **元素点击**: 通过CSS选择器点击页面元素
- **表单填写**: 填写表单或选择选项
- **键盘操作**: 模拟键盘输入
- **获取页面内容**: 提取页面文本和HTML
- **获取元素**: 获取页面中的特定元素
- **交互式元素识别**: 自动识别页面中的交互式元素

### 媒体和网络
- **截图**: 截取整个页面或特定元素

## 🚀 快速开始

### 前置要求

- Python 3.9+ 和 pip/poetry/uv
- Chrome/Chromium浏览器

### 安装步骤

#### 1. 安装Chrome扩展

```bash
cd extension
pnpm install
pnpm run build

# 或者去releases中下载指定版本
```

然后在Chrome浏览器中:
1. 打开 `chrome://extensions/`
2. 启用"开发者模式"
3. 点击"加载已解压的扩展程序"

#### 2. 运行服务

```json
{
  "mcpServers": {
    "nep-browser-engine": {
      "type": "stdio",
      "command": "uvx",
      "args": ["nep-browser-engine"]
    }
  }
}
```

#### 3. 连接扩展和服务

点击浏览器中的扩展图标，连接到WebSocket服务。

## 📝 使用说明

### 与MCP协议客户端一起使用

可以将本服务与支持MCP协议的AI客户端一起使用，例如Claude、CherryStudio等。


## 🛠️ 可用工具列表

以下是主要的可用工具：

### 浏览器管理
- `get_windows_and_tabs`: 获取所有打开的窗口和标签页
- `browser_navigate`: 导航到URL或刷新当前标签页
- `browser_close_tabs`: 关闭特定标签页或窗口
- `browser_go_back_or_forward`: 浏览器历史前进或后退

### 页面交互
- `browser_click_element`: 点击页面元素
- `browser_fill_or_select`: 填写表单或选择选项
- `browser_get_elements`: 获取页面元素
- `browser_keyboard`: 模拟键盘输入
- `browser_get_web_content`: 获取网页内容
- `browser_screenshot`: 截取页面截图

## 🔧 开发指南

### Python服务端开发

1. 确保安装了所有依赖
2. 可以通过修改 `app/src/nep_browser_engine/config.py` 来配置WebSocket端口等参数
3. 运行时可以通过参数指定传输协议: `python -m nep_browser_engine.app --transport stdio`

### Chrome扩展开发

1. 修改代码后运行 `pnpm run build` 重新构建扩展
2. 扩展会自动重新加载（如果在开发者模式下）
3. WebSocket默认连接地址为 `ws://localhost:18765`

## 📋 注意事项

- 本项目仍在开发中，可能存在一些bug和不完善的地方
- 使用前请确保理解所有工具的功能和潜在风险
- 请勿将本项目用于任何非法或未经授权的活动

## 🤝 贡献

欢迎提交issue和PR来帮助改进这个项目！

## 鸣谢
本项目参考 [hangwin/mcp-chrome](https://github.com/hangwin/mcp-chrome)

## 📄 许可证

[MIT License](LICENSE)