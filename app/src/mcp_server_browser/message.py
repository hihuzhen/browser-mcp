from loguru import logger
from typing import Dict, Any, Optional
from enum import Enum
from datetime import datetime
from dataclasses import dataclass, field


class WebSocketMessageType(Enum):
    """WebSocket消息类型枚举"""
    PING = 'ping'
    PONG = 'pong'
    CALL_TOOL = 'call_tool'
    CALL_TOOL_RESPONSE = 'call_tool_response'
    ERROR = 'error'


@dataclass
class ToolResponseMessage:
    response_to_request_id: str
    is_success: bool
    payload: Any
    error: Optional[str] = None
    type: str = field(default=WebSocketMessageType.CALL_TOOL_RESPONSE.value)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class WebSocketMessage:
    """WebSocket消息数据结构"""
    type: WebSocketMessageType
    payload: Optional[Any] = None
    request_id: Optional[str] = None
    response_to_request_id: Optional[str] = None
    error: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WebSocketMessage":
        """从字典创建WebSocket消息对象"""
        # 处理type字段
        message_type = None
        type_value = data.get("type")
        if type_value:
            for t in WebSocketMessageType:
                if t.value == type_value:
                    message_type = t
                    break

        if message_type is None:
            raise ValueError(f"Invalid message type: {type_value}")

        return cls(
            type=message_type,
            payload=data.get("payload"),
            request_id=data.get("requestId"),
            response_to_request_id=data.get("responseToRequestId"),
            error=data.get("error")
        )

    def to_dict(self) -> dict:
        return {"type": self.type.value, "payload": self.payload, "requestId": self.request_id,
                "responseToRequestId": self.response_to_request_id, "error": self.error}

    def to_tool_message(self) -> Optional[ToolResponseMessage]:
        try:
            if self.type != WebSocketMessageType.CALL_TOOL_RESPONSE:
                return None
            try:
                is_success = (self.payload.get("status") == "success") and not(self.payload.get("data").get("isError"))
                error = self.payload.get("error")
                payload = self.payload.get("data").get("content")
            except Exception as e:  # noqa
                is_success = False
                error = str(e)
                payload = {}
            message = ToolResponseMessage(response_to_request_id=self.response_to_request_id, is_success=is_success,
                                          payload=payload, error=error)
            return message
        except Exception as e:
            logger.error(e)
            return None

    def get_response_message(self) -> Optional["WebSocketMessage"]:
        try:
            if self.type != WebSocketMessageType.PING:
                return None
            return WebSocketMessage(type=WebSocketMessageType.PONG)
        except Exception as e:
            logger.error(e)
            return None
