from pathlib import Path
import fitz
from docx import Document


def load_markdown(filepath: str) -> str:
    return Path(filepath).read_text(encoding="utf-8")


def load_txt(filepath: str) -> str:
    return Path(filepath).read_text(encoding="utf-8")


def load_pdf(filepath: str) -> str:
    doc = fitz.open(filepath)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text


def load_docx(filepath: str) -> str:
    doc = Document(filepath)
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


LOADERS = {
    ".md": load_markdown,
    ".txt": load_txt,
    ".pdf": load_pdf,
    ".docx": load_docx,
}


def load_document(filepath: str) -> str | None:
    suffix = Path(filepath).suffix.lower()
    loader = LOADERS.get(suffix)
    if not loader:
        return None
    return loader(filepath)


def load_all_documents(docs_dir: str) -> list[dict]:
    docs = []
    for p in Path(docs_dir).rglob("*"):
        if p.is_file() and p.suffix.lower() in LOADERS:
            content = load_document(str(p))
            if content and content.strip():
                docs.append({"path": str(p), "name": p.name, "content": content})
    return docs
