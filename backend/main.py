from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.auth import auth
from routers.llm import llm
from routers.user import profile, tokens, user
from database import database
from routers.conversations import conversations
import os
from dotenv import load_dotenv
load_dotenv

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("DEV_SERVER"), os.getenv("FRONT-END-PROD")],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "PUT"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(profile.router, prefix="/profile", tags=["profile"])
app.include_router(llm.router, prefix="/llm", tags=["llm"] )
app.include_router(tokens.router, prefix="/tokens", tags=["tokens"])
app.include_router(user.router, prefix="/user", tags=["user"])
app.include_router(conversations.router, prefix="/conversation", tags=["conversation"])





@app.get("/")
async def root():
    return {"message": "Welcome to your API"}

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()