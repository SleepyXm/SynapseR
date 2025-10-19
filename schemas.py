from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any, Dict, List
from uuid import UUID

class UserCreate(BaseModel):
    username: str
    password: str
    hf_token: Optional[list[str]] = []  # Will store encrypted token

class UserLogin(BaseModel):
    username: str
    password: str

class HFTokenRequest(BaseModel):
    hf_token: str

class UserOut(BaseModel):
    id: str
    username: str
    password: str
    created_at: datetime

    class Config:
        orm_mode = True

class FavLLM(BaseModel):
    hf_id: str

class AddLLMRequest(BaseModel):
    llm_id: str
    llm_name: str

class Message(BaseModel):
    role: str
    content: str

class StoredMessage(BaseModel):
    id: str
    message: Dict[str, Any]
    role: str
    created_at: datetime
    metadata: Dict[str, Any] = {}

    class Config:
        orm_mode = True

class Request(BaseModel):
    modelId: Optional[str] = None
    hfToken: str

class ChatRequest(Request):
    conversation: List[Message]

class EmbedRequest(Request):
    files: List[str]

class CreateConversationRequest(BaseModel):
    title: str
    llm_model: str