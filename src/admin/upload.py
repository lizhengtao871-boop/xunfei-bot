from fastapi import APIRouter, UploadFile, File
from pathlib import Path
from src.config import config
from src.rag.retriever import build_knowledge_base

router = APIRouter(prefix="/admin", tags=["知识库"])


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename:
        return {"error": "文件名为空"}
    filepath = Path(config.DOCS_DIR) / file.filename
    content = await file.read()
    filepath.write_bytes(content)
    build_knowledge_base()
    return {"ok": True, "file": file.filename, "path": str(filepath)}
