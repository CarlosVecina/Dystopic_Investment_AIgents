from datetime import datetime
from pydantic import BaseModel, Field


class Message(BaseModel):
    """Single conversation message"""

    content: str
    role: str  # 'user', 'assistant', or 'system'
    timestamp: datetime = Field(default_factory=datetime.now)


class ConversationMemory(BaseModel):
    """Stores conversation history"""

    messages: list[Message] = Field(default_factory=list)
    max_messages: int = 100

    def add_message(self, content: str, role: str) -> None:
        """Add a new message to the conversation history"""
        self.messages.append(Message(content=content, role=role))

        # Remove oldest messages if exceeding max_messages
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages :]

    def get_history(self, limit: int | None = None) -> list[Message]:
        """Retrieve recent conversation history"""
        return self.messages[-limit:] if limit else self.messages
