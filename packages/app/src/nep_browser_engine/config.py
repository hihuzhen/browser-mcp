import os

from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()


class Config(BaseModel):
    WebSocketPort: int = Field(default=os.getenv("WEBSOCKET_PORT", 18765))


config = Config()