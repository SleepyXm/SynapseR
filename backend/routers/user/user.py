from fastapi import APIRouter, Depends
from database import database
from routers.auth.auth_utils import get_current_user
from schemas import FavLLM
from uuid import uuid4

router = APIRouter()

@router.post("/add_fav")
async def add_fav(req: FavLLM, current_user: dict = Depends(get_current_user)):
    # 1️⃣ Check if the LLM already exists in the database
    query_check = "SELECT id FROM llms WHERE name = :hf_id"
    llm = await database.fetch_one(query=query_check, values={"hf_id": req.hf_id})

    # 2️⃣ If not, insert it with a UUID as primary key
    if not llm:
        llm_uuid = str(uuid4())
        query_insert = """
        INSERT INTO llms (id, name)
        VALUES (:llm_id, :name)
        """
        await database.execute(query=query_insert, values={
            "llm_id": llm_uuid,  # real UUID
            "name": req.hf_id     # store Hugging Face ID here
        })
        llm_id_to_use = llm_uuid
    else:
        llm_id_to_use = llm["id"]

    # 3️⃣ Add the LLM UUID to the user's favorites if not already present
    query_update = """
    UPDATE users
    SET favorites = array_append(favorites, :llm_id)
    WHERE id = :user_id
      AND NOT (:llm_id = ANY(favorites))
    """
    await database.execute(query=query_update, values={
        "llm_id": llm_id_to_use,
        "user_id": current_user["id"]
    })

    return {"status": "success", "message": "Favourite added"}




@router.post("/remove_fav")
async def remove_fav(req: FavLLM, current_user: dict = Depends(get_current_user)):
    # 1️⃣ Look up the LLM in the database
    query_check = "SELECT id FROM llms WHERE name = :hf_id"
    llm = await database.fetch_one(query=query_check, values={"hf_id": req.hf_id})

    if not llm:
        return {"status": "error", "message": "LLM not found"}

    llm_id_to_remove = llm["id"]

    # 2️⃣ Remove the LLM UUID from the user's favorites
    query_update = """
    UPDATE users
    SET favorites = array_remove(favorites, :llm_id)
    WHERE id = :user_id
      AND :llm_id = ANY(favorites)
    """
    await database.execute(query=query_update, values={
        "llm_id": llm_id_to_remove,
        "user_id": current_user["id"]
    })

    return {"status": "success", "message": "Favourite removed"}