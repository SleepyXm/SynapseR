from fastapi import APIRouter, HTTPException, Depends, Cookie
from database import database
from routers.auth.auth_utils import get_current_user
from schemas import HFTokenRequest
import json

router = APIRouter()


@router.post("/hf_token")
async def add_hf_token(req: HFTokenRequest, current_user: dict = Depends(get_current_user)):
    query = "SELECT hf_tokens FROM users WHERE id = :user_id"
    db_user = await database.fetch_one(query=query, values={"user_id": current_user["id"]})
    current_tokens = json.loads(db_user["hf_tokens"]) if db_user["hf_tokens"] else []

    if req.hf_token in current_tokens:
        raise HTTPException(status_code=400, detail="Token already exists")

    current_tokens.append(req.hf_token)
    update_query = "UPDATE users SET hf_tokens = :hf_tokens WHERE id = :user_id"
    await database.execute(query=update_query, values={"hf_tokens": json.dumps(current_tokens), "user_id": current_user["id"]})

    return {"message": "HF Token added successfully", "hf_tokens": current_tokens}


@router.delete("/hf_token")
async def remove_hf_token(req: HFTokenRequest, current_user: dict = Depends(get_current_user)):
    query = "SELECT hf_tokens FROM users WHERE id = :user_id"
    db_user = await database.fetch_one(query=query, values={"user_id": current_user["id"]})
    current_tokens = json.loads(db_user["hf_tokens"]) if db_user["hf_tokens"] else []

    if req.hf_token not in current_tokens:
        raise HTTPException(status_code=404, detail="Token not found")

    current_tokens.remove(req.hf_token)
    update_query = "UPDATE users SET hf_tokens = :hf_tokens WHERE id = :user_id"
    await database.execute(query=update_query, values={"hf_tokens": json.dumps(current_tokens), "user_id": current_user["id"]})

    return {"message": "HF Token deleted successfully", "hf_tokens": current_tokens}