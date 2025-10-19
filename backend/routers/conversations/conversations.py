from fastapi import APIRouter, Body, Depends
from routers.auth.auth_utils import get_current_user
from schemas import CreateConversationRequest
from typing import List, Dict, Any
from helpers import ConversationManager

router = APIRouter()

@router.post("/{conversation_id}/chunk")
async def save_chunk(
    conversation_id: str,
    messages: List[Dict[str, Any]] = Body(...),
    current_user: dict = Depends(get_current_user),
):
    manager = ConversationManager(conversation_id, current_user["id"])
    await manager.load()
    await manager.append(messages)
    await manager.persist()
    return {"status": "ok", "chunk_size": len(messages)}

@router.get("/{conversation_id}/chunk")
async def load_chunks(conversation_id: str, current_user: dict = Depends(get_current_user)):
    manager = ConversationManager(conversation_id, current_user["id"])
    await manager.load()
    return await manager.to_dict()

@router.post("/create")
async def create_conversation(req: CreateConversationRequest, current_user: dict = Depends(get_current_user)):
    manager = ConversationManager(conversation_id="", user_id=current_user["id"])
    new_id = await manager.create(req.llm_model)
    return {"id": new_id, "title": None}

@router.get("/list")
async def list_conversations(current_user: dict = Depends(get_current_user)):
    manager = ConversationManager(conversation_id="", user_id=current_user["id"])
    return {"conversations": await manager.list_for_user()}