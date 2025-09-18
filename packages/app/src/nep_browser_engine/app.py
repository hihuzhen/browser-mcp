import argparse
import sys
import uvicorn
import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from nep_browser_engine.mcp_server.mcp import mcp
from nep_browser_engine.websockets_services.websocket_server import WebSocketServer

@asynccontextmanager
async def web_server_lifespan(app) -> AsyncIterator[None]:
    """Manage application lifecycle with type-safe context."""
    # Initialize on startup
    websocket_server = await WebSocketServer.get_instance()
    try:
        await websocket_server.start()
        async with mcp.session_manager.run():
            yield
    finally:
        # Cleanup on shutdown
        await websocket_server.stop()


async def run(transport: str = "stdio", port: int = 8000):
    if transport == "stdio":
        websocket_server = await WebSocketServer.get_instance()
        try:
            await websocket_server.start()
            await mcp.run_stdio_async()
        finally:
            await websocket_server.stop()
    else:
        starlette_app = mcp.streamable_http_app()
        starlette_app.router.lifespan_context = web_server_lifespan
        config = uvicorn.Config(starlette_app, host="127.0.0.1", port=port)
        server = uvicorn.Server(config)
        await server.serve()

def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="Milu MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "streamable-http"],
        default="stdio",
        help="Transport protocol to use (default: stdio)"
    )
    parser.add_argument(
        "--port",
        default=8000,
        help="streamable-http server port"
    )
    args = parser.parse_args()
    transport = args.transport
    port = args.port
    if len(sys.argv) == 1 or args.transport == "stdio":
        transport = "stdio"
    asyncio.run(run(transport, port))



if __name__ == '__main__':
    main()
