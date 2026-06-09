from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Literal
from uuid import UUID
from datetime import datetime


class ChatMessage(BaseModel):
    role: Literal["system", "user"] = Field(
        ..., description="The role of the message author"
    )
    content: str = Field(..., description="The content of the message")
    
    class Config:
        extra = "forbid"


class ChatMetaData(BaseModel):

    user_id: UUID       = Field(..., description="User Identifier")
    session_name: str   = Field(..., description="Session Name")
    session_id: UUID    = Field(..., description="session Identifier")
    conv_id: UUID       = Field(..., description="Conversation Identifier")

    class Config:
        extra = "forbid"



class ChatRequest(BaseModel):

    conversation: ChatMessage = Field(
        ..., description="Current Coversation of the user"
    )

    conversation_history: List[ChatMessage] = Field(
        ..., description="List of messages in the conversation"
    )

    metadata: Optional[ChatMetaData] = Field(
        None, description="Session and context metadata"
    )

    stream: bool = Field(
        default=False, description="Streaming disabled - always returns complete response"
    )

    requested_at: datetime = Field(
        ..., description="timestamp when this message is posted"
    )

    class Config:
        json_schema_extra = {
            "example" : {
                "conversation": {
                        "role": "user",
                        "content": "Compare Sales for previous financial year across months."
                    },
                "conversation_history": {},
                
                "metadata": {
                    "user_id": "user_123",
                    "session_name": "Analyse Sales",
                    "session_id": "session_123",
                    "conv_id": "conv_123"
                },

                "stream": False
                
            }
        }

        extra = "forbid"
