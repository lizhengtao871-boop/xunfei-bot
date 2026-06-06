import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.config import config
from src.db.models import engine, Base

# Isolate potentially failing imports
try:
    from src.wx_gateway.callback import router as wx_router
except Exception as e:
    print(f"[WARN] wx_gateway import failed: {e}", file=sys.stderr)
    from fastapi import APIRouter
    wx_router = APIRouter()

try:
    from src.admin.dashboard import router as admin_router
    from src.admin.upload import router as upload_router
except Exception as e:
    print(f"[WARN] admin import failed: {e}", file=sys.stderr)
    from fastapi import APIRouter
    admin_router = APIRouter()
    upload_router = APIRouter()

try:
    from src.router.intent import process_message
except Exception as e:
    print(f"[WARN] router.intent import failed: {e}", file=sys.stderr)
    process_message = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[startup] initializing...", file=sys.stderr)
    os.makedirs(config.DOCS_DIR, exist_ok=True)
    os.makedirs(config.CHROMA_PERSIST_DIR, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    try:
        from src.db.init_db import init_db
        init_db()
    except Exception as e:
        print(f"[startup] init_db error: {e}", file=sys.stderr)
    print("[startup] complete", file=sys.stderr)
    yield


app = FastAPI(title="讯飞协会管理智能体", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(wx_router)
app.include_router(admin_router)
app.include_router(upload_router)


class ChatRequest(BaseModel):
    text: str
    user_name: str = "测试用户"


@app.post("/chat")
def chat(req: ChatRequest):
    if process_message:
        reply = process_message(req.text, req.user_name)
    else:
        reply = "服务初始化中，请稍后再试。"
    return {"reply": reply}


@app.get("/")
def root():
    return {"message": "讯飞协会管理智能体已运行", "health": "/health"}


@app.get("/health")
def health():
    return {"status": "ok", "service": "讯飞协会管理智能体"}


@app.get("/ping")
def ping():
    from datetime import datetime
    return {"pong": True, "time": datetime.now().isoformat()}
