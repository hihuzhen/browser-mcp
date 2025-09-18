import asyncio
import json
import uuid
from typing import Optional, Any, ClassVar

import websockets
from loguru import logger
from websockets.asyncio.server import ServerConnection
from websockets.exceptions import WebSocketException

from nep_browser_engine.config import config
from nep_browser_engine.message import WebSocketMessage, WebSocketMessageType, ToolResponseMessage
from nep_browser_engine.websockets_services.connection_manager import ConnectionManager
from nep_browser_engine.websockets_services.message_pool import ToolMessagePool


class WebSocketServer:
    """WebSocket 服务器主类，采用单例模式设计以确保全局唯一实例"""

    # 单例模式实现
    _instance: ClassVar[Optional['WebSocketServer']] = None
    _lock: ClassVar[asyncio.Lock] = asyncio.Lock()

    def __init__(self):
        """
        初始化 WebSocket 服务器
        注意：应通过get_instance()获取实例而非直接实例化
        """
        # 防止直接实例化
        if WebSocketServer._instance is not None:
            raise RuntimeError("请使用WebSocketServer.get_instance()获取单例实例")

        self.config = config
        self.connection_manager = ConnectionManager()
        self.tool_message_pool = ToolMessagePool()
        self._server: Optional[websockets.server] = None
        self._running: bool = False

    @classmethod
    async def get_instance(cls) -> 'WebSocketServer':
        """
        获取WebSocketServer的单例实例
        
        :return: WebSocketServer的唯一实例
        """
        async with cls._lock:
            if cls._instance is None:
                # 创建新实例
                cls._instance = cls()
        return cls._instance

    async def handle_connection(self, websocket: ServerConnection):
        """处理WebSocket连接"""
        connection_id = str(uuid.uuid4())

        try:
            # 注册连接
            await self.connection_manager.register_connection(websocket, connection_id)

            # 发送连接确认消息
            ping_message = WebSocketMessage(
                type=WebSocketMessageType.PING,
                request_id=str(uuid.uuid4())
            )
            await self.connection_manager.send_message(ping_message)

            # 处理消息
            async for message in websocket:
                logger.info(f"连接 {connection_id} 收到消息: {message[:200]}{'...' if len(message) > 200 else ''}")
                ws_message = WebSocketMessage.from_dict(json.loads(message))
                # 根据消息类型进行不同处理
                await self._process_websocket_message(ws_message)

        except WebSocketException as e:
            logger.error(f"连接 {connection_id} WebSocket异常: {e}")
        except Exception as e:
            logger.error(f"连接 {connection_id} 处理错误: {e}")
            logger.exception(e)


    async def _process_websocket_message(self, ws_message: WebSocketMessage):
        """处理WebSocket消息"""
        # 对于to_tool_message成功的消息，放入消息池
        tool_message: Optional[ToolResponseMessage] = ws_message.to_tool_message()
        if tool_message:
            logger.info(f"将工具响应消息添加到消息池: {tool_message.response_to_request_id}")
            await self.tool_message_pool.add_message(tool_message)
            return

        # 对于get_response_message成功的直接回复
        response_message = ws_message.get_response_message()
        if response_message:
            logger.info("发送响应消息")
            await self.connection_manager.send_message(response_message)
            return

        # 其他类型的消息打日志处理
        logger.info(f"收到未特殊处理的消息类型: {ws_message.type.value}")
        
    async def broadcast_tool_request(self, name: str, tool_args: Any) -> str:
        try:
            tool_request = WebSocketMessage.from_dict(
                {
                    "type": WebSocketMessageType.CALL_TOOL.value,
                    "requestId": str(uuid.uuid4()),
                    "payload": {
                        "name": name,
                        "args": tool_args
                    }
                }
            )
            is_sent = await self.connection_manager.send_message(tool_request)
            if not is_sent:
                return ""
            logger.info(f"广播ToolRequestMessage消息: {tool_request.request_id}")
            return tool_request.request_id
        except Exception as e:
            logger.error(f"广播ToolRequestMessage消息失败: {e}")
            return ""

    async def get_tool_resp_message(self, request_id: str, timeout: float = 30.0) -> Optional[ToolResponseMessage]:
        """
        从消息池获取消息
        :param request_id: 消息ID
        :param timeout: 超时时间（秒）
        :return: 消息对象
        """
        message = await self.tool_message_pool.get_message(request_id, timeout)
        if not message:
            raise TimeoutError(f"获取消息 {request_id} 超时或消息不存在")
        return message

    async def start(self):
        """启动 WebSocket 服务器"""
        if self._running:
            logger.warning("服务器已在运行")
            return

        # 启动 WebSocket 服务器，直接使用handle_connection方法
        self._server = await websockets.serve(
            self.handle_connection,
            "localhost",
            self.config.WebSocketPort
        )

        self._running = True
        logger.info(f"WebSocket服务器已启动，监听端口: {self.config.WebSocketPort}")

    async def stop(self):
        """停止 WebSocket 服务器"""
        if not self._running:
            return

        logger.info("正在停止 WebSocket 服务器...")

        # 关闭服务器
        if self._server:
            self._server.close()

        self._running = False
        logger.info("WebSocket 服务器已停止")
