import asyncio
import json
from loguru import logger
from websockets.asyncio.server import ServerConnection
from websockets.exceptions import ConnectionClosed

from nep_browser_engine.message import WebSocketMessage


class ConnectionManager:
    """WebSocket 连接管理器，确保只保持一个有效连接"""
    
    def __init__(self):
        self.connections: dict[str, ServerConnection] = {}
        self._lock = asyncio.Lock()
        
    async def register_connection(self, websocket: ServerConnection, connection_id: str) -> bool:
        """
        注册新连接
        :param websocket: WebSocket 连接对象
        :param connection_id: 连接标识符
        :return: 是否成功注册
        """
        self.connections[connection_id] = websocket
        logger.info(f"注册新连接: {connection_id}")
        return True
    
    async def unregister_connection(self, connection_id: str) -> bool:
        """
        注销连接
        :param connection_id: 连接标识符
        :return: 是否成功注销
        """
        if connection_id in self.connections:
            del self.connections[connection_id]
        return False

    
    async def send_message(self, message: WebSocketMessage) -> bool:
        """
        向当前连接发送消息
        :param message: 要发送的消息
        :return: 是否成功发送
        """
        async with self._lock:

            connection_keys = list(self.connections.keys())
            logger.info(f"start send current connections: {len(connection_keys)}")
            msg = json.dumps(message.to_dict())
            for connection_id in connection_keys:
                try:
                    connection = self.connections[connection_id]
                    await connection.send(msg)
                    logger.debug(f"消息已发送到连接 {connection_id}")
                    logger.info(f"end send current connections: {len(connection_keys)}")
                    return True
                except ConnectionClosed:
                    logger.error(f"连接 {connection_id} 已关闭，无法发送消息")
                    await self.unregister_connection(connection_id)
                except Exception as e:
                    logger.error(f"发送消息时出错: {e}")
            logger.info(f"end send current connections: {len(connection_keys)}")
            return False
