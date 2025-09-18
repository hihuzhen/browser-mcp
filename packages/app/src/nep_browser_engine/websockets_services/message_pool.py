import asyncio
from collections import OrderedDict
from copy import deepcopy
from datetime import datetime, timedelta
from typing import Dict, Optional

from loguru import logger

from nep_browser_engine.message import ToolResponseMessage


class PooledMessage:
    """池化消息，包含消息对象和过期时间"""

    def __init__(self, message: ToolResponseMessage, expiry_time: datetime):
        self.message = message
        self.expiry_time = expiry_time

    @property
    def is_expired(self) -> bool:
        """检查消息是否已过期"""
        return datetime.now() > self.expiry_time


class ToolMessagePool:
    """消息池管理器，处理消息存储、过期和检索"""

    def __init__(self, default_ttl_seconds: int = 300):
        """
        初始化消息池
        :param default_ttl_seconds: 默认消息生存时间（秒）
        """
        self._messages: Dict[str, PooledMessage] = OrderedDict()
        self._default_ttl = default_ttl_seconds
        self._lock = asyncio.Lock()

    async def add_message(self, message: ToolResponseMessage, ttl_seconds: Optional[int] = None) -> str:
        """
        添加消息到消息池
        :param message: 要添加的消息
        :param ttl_seconds: 消息生存时间（秒），如果不指定则使用默认值
        :return: 消息ID
        """
        ttl = ttl_seconds if ttl_seconds is not None else self._default_ttl
        expiry_time = datetime.now() + timedelta(seconds=ttl)

        async with self._lock:
            pooled_message = PooledMessage(
                message=message,
                expiry_time=expiry_time
            )
            message_id = message.response_to_request_id
            if not message_id:
                return ""
            self._messages[message_id] = pooled_message
            if self.size > 100:
                expired_ids = [msg_id for msg_id, pooled_msg in self._messages.items() if pooled_msg.is_expired]
                for msg_id in expired_ids:
                    del self._messages[msg_id]
            logger.info(f"消息 {message_id} 已添加到消息池，过期时间: {expiry_time}")
            return message_id

    async def get_message(self, message_id: str, timeout: float = 30.0, mark_as_retrieved: bool = True) -> Optional[
        ToolResponseMessage]:
        """
        从消息池获取消息，支持超时等待
        :param message_id: 消息ID
        :param timeout: 超时时间（秒）
        :param mark_as_retrieved: 是否标记消息为已检索
        :return: 消息对象
        :raises TimeoutError: 超时未找到指定消息时抛出异常
        """
        start_time = asyncio.get_event_loop().time()

        while True:
            # 检查消息是否存在
            if message_id in self._messages:
                pooled_msg = deepcopy(self._messages[message_id])

                # 检查消息是否已过期
                if pooled_msg.is_expired:
                    logger.warning(f"消息 {message_id} 已过期")
                    del self._messages[message_id]
                    return None

                if mark_as_retrieved:
                    pooled_msg.retrieved = True

                logger.debug(f"获取消息 {message_id}")
                return pooled_msg.message

            # 检查是否超时
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed >= timeout:
                logger.error(f"获取消息 {message_id} 超时 ({timeout}秒)")
                raise TimeoutError(f"等待消息 {message_id} 超时")

            await asyncio.sleep(0.2)

    @property
    def size(self) -> int:
        """获取消息池当前大小"""
        return len(self._messages)
