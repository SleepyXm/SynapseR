from schemas import StoredMessage
from typing import List, Dict, Any
from datetime import datetime
import zlib
import json
import uuid
from database import database
from fastapi import HTTPException
import asyncio

def compress_messages(messages: List["StoredMessage"]) -> bytes:
    return zlib.compress(json.dumps(
        [m.dict() for m in messages],
        default=lambda o: o.isoformat() if isinstance(o, datetime) else o
    ).encode("utf-8"))

def decompress_messages(data: bytes) -> List["StoredMessage"]:
    if not data:
        return []
    raw = zlib.decompress(data)
    items = json.loads(raw)
    # convert created_at back into datetime objects
    for m in items:
        if "created_at" in m and isinstance(m["created_at"], str):
            try:
                m["created_at"] = datetime.fromisoformat(m["created_at"])
            except Exception:
                pass
    return [StoredMessage(**m) for m in items]

def append_messages(existing_compressed: bytes, new_messages: List[Dict[str, Any]]) -> bytes:
    messages = decompress_messages(existing_compressed)
    now = datetime.utcnow()
    messages.extend([
        StoredMessage(
            id=str(uuid.uuid4()),
            message=m,  # raw JSON from frontend
            role=m.get("role", "user"),
            created_at=now
        ) for m in new_messages
    ])
    return compress_messages(messages)


# Get Helpers

async def get_conversation_messages(conversation_id: str, user_id: str):
    query = "SELECT compressed_messages, user_id FROM conversations WHERE id = :conversation_id"
    row = await database.fetch_one(query=query, values={"conversation_id": conversation_id})

    if not row or not row["compressed_messages"]:
        raise HTTPException(status_code=404, detail="No conversation found")

    if row["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="You do not own this conversation")

    return decompress_messages(row["compressed_messages"])


class ConversationManager:
    """Centralized async-safe manager for conversation storage and ephemeral LLM memory."""

    def __init__(self, conversation_id: str, user_id: str):
        self.conversation_id = conversation_id
        self.user_id = user_id
        self.messages: List[StoredMessage] = []
        self.lock = asyncio.Lock()
        self.loaded = False

    async def to_dict(self):
        async with self.lock:
            return {"messages": [m.dict() for m in self.messages]}

    # --- Core DB operations ---
    async def load(self):
        async with self.lock:
            if self.loaded:
                return
            try:
                self.messages = await get_conversation_messages(self.conversation_id, self.user_id)
            except HTTPException as e:
                if e.status_code == 404:
                    self.messages = []  # <-- empty conversation
                else:
                    raise
            self.loaded = True

    async def append(self, new_messages: List[Dict[str, Any]]):
        async with self.lock:
            now = datetime.utcnow()
            for m in new_messages:
                self.messages.append(
                    StoredMessage(
                        id=str(uuid.uuid4()),
                        message=m,
                        role=m.get("role", "user"),
                        created_at=now,
                    )
                )

    async def persist(self):
        async with self.lock:
            compressed = compress_messages(self.messages)
            await database.execute(
                """
                UPDATE conversations
                SET compressed_messages = :compressed,
                    updated_at = NOW()
                WHERE id = :id
                """,
                {"compressed": compressed, "id": self.conversation_id},
            )

    async def create(self, llm_model: str):
        conversation_id = str(uuid.uuid4())
        now = datetime.utcnow()
        await database.execute(
            """
            INSERT INTO conversations (id, user_id, llm_model, title, created_at, updated_at)
            VALUES (:id, :user_id, :llm_model, NULL, :created_at, :updated_at)
            """,
            {
                "id": conversation_id,
                "user_id": self.user_id,
                "llm_model": llm_model,
                "created_at": now,
                "updated_at": now,
            },
        )
        self.conversation_id = conversation_id
        return conversation_id

    async def list_for_user(self):
        rows = await database.fetch_all(
            """
            SELECT id, title, llm_model, created_at, updated_at
            FROM conversations
            WHERE user_id = :user_id
            ORDER BY updated_at DESC
            """,
            {"user_id": self.user_id},
        )
        return [
            {"id": r["id"], "title": r["title"], "llm_model": r["llm_model"]}
            for r in rows
        ]
    
    

    # --- Ephemeral LLM memory ---
    async def get_memory_snapshot(self, recent_n: int = 20) -> list[dict]:
        """Return last N messages formatted for LLM consumption."""

        print(f"[ConversationManager] Loaded {len(self.messages)} messages for conversation {self.conversation_id}")

        await self.load()
        snapshot = []
        recent_messages = self.messages[-recent_n:]
        for m in recent_messages:
            snapshot.append({
                "role": m.role,
                "content": m.message.get("content", "")
            })
        # Optional system prompt
        system_prompt = "You are an assistant aware of the recent conversation context with the user."
        snapshot.insert(0, {"role": "system", "content": system_prompt})
        return snapshot