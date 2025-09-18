import json
import anyio
from typing import Any

from nep_browser_engine.message import ToolResponseMessage
from nep_browser_engine.websockets_services.websocket_server import WebSocketServer

_tool_call_lock = anyio.Lock()

async def call_tool(tool_name: str, tool_args: dict) -> Any:
    async with _tool_call_lock:
        websocket_server = await WebSocketServer.get_instance()
        request_id = await websocket_server.broadcast_tool_request(name=tool_name, tool_args=tool_args)
        if not request_id:
            raise ValueError(f"工具 {tool_name} 调用失败: connection failed.")
        tool_resp_msg: ToolResponseMessage = await websocket_server.get_tool_resp_message(request_id=request_id)
        if not tool_resp_msg.is_success:
            raise ValueError(f"工具 {tool_name} 调用失败: {tool_resp_msg.error}")
        return json.loads(tool_resp_msg.payload[0].get("text"))
