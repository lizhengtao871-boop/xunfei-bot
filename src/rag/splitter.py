from langchain_text_splitters import RecursiveCharacterTextSplitter

_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=100,
    separators=["\n\n", "\n", "。", ".", "；", ";", " "],
)


def split_text(text: str) -> list[str]:
    return _splitter.split_text(text)


def split_documents(docs: list[dict]) -> list[dict]:
    chunks = []
    for doc in docs:
        for i, chunk in enumerate(split_text(doc["content"])):
            chunks.append({
                "source": doc["name"],
                "path": doc["path"],
                "chunk_index": i,
                "content": chunk,
            })
    return chunks
