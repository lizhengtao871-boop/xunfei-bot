from src.agent.tool_registry import register_tool
from src.rag.retriever import search


@register_tool(
    name="search_knowledge",
    description="语义搜索协会知识库，获取规章制度、活动流程、管理规范等信息。",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "搜索查询，用自然语言描述要查找的内容"},
        },
        "required": ["query"],
    },
)
def search_knowledge(query: str) -> str:
    results = search(query, top_k=5)
    if not results:
        return "未在知识库中找到相关内容。"
    lines = []
    for i, r in enumerate(results, 1):
        lines.append(f"**片段 {i}** (来源: {r['source']}):\n{r['content']}\n")
    return "\n".join(lines)
