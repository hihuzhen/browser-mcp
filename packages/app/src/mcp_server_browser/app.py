import argparse
import sys
from mcp_server_browser.mcp_server.mcp import mcp


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="XiaoJi MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable-http"],
        default="stdio",
        help="Transport protocol to use (default: stdio)"
    )

    # 如果没有参数，则使用默认值
    if len(sys.argv) == 1:
        mcp.run("stdio")
    else:
        args = parser.parse_args()
        mcp.run(args.transport)


if __name__ == '__main__':
    main()
