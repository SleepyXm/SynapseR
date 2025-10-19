from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Request, HTTPException, status
from database import database
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 240))


def create_access_token(username: str):
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": username, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None


async def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Missing authentication token")

    if token.startswith("Bearer "):
        token = token[len("Bearer "):]

    user_id = verify_token(token)  # this returns ID
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    query = "SELECT * FROM users WHERE id = :id"
    user = await database.fetch_one(query=query, values={"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user