import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from src.wx_gateway.callback import router as wx_router
from src.db.models import engine, Base
from src.admin.dashboard import router as admin_router
from src.admin.upload import router as upload_router
from src.router.intent import process_message
from src.config import config

app = FastAPI(title="讯飞协会管理智能体", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(wx_router)
app.include_router(admin_router)
app.include_router(upload_router)


@app.on_event("startup")
def startup():
    # Ensure data directories exist (important for Render ephemeral filesystem)
    os.makedirs(config.DOCS_DIR, exist_ok=True)
    os.makedirs(config.CHROMA_PERSIST_DIR, exist_ok=True)

    # Create database tables
    Base.metadata.create_all(bind=engine)

    # Initialize seed data
    from src.db.init_db import init_db
    init_db()

    # Build knowledge base if documents exist
    from src.rag.retriever import _INDEX_PATH
    if not _INDEX_PATH.exists():
        from src.rag.retriever import build_knowledge_base
        build_knowledge_base()


class ChatRequest(BaseModel):
    text: str
    user_name: str = "测试用户"


@app.post("/chat")
def chat(req: ChatRequest):
    reply = process_message(req.text, req.user_name)
    return {"reply": reply}


@app.get("/health")
def health():
    return {"status": "ok", "service": "讯飞协会管理智能体"}


if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
