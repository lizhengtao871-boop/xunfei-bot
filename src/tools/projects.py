from src.agent.tool_registry import register_tool
from src.db.models import SessionLocal, Project


@register_tool(
    name="list_projects",
    description="查询项目列表及状态。可按来源或状态筛选。",
    parameters={
        "type": "object",
        "properties": {
            "source": {"type": "string", "enum": ["internal", "external"], "description": "内部孵化或外部承接"},
            "status": {"type": "string", "description": "项目状态: planning/active/done/archived"},
        },
    },
)
def list_projects(source: str | None = None, status: str | None = None) -> str:
    db = SessionLocal()
    try:
        q = db.query(Project)
        if source:
            q = q.filter(Project.source == source)
        if status:
            q = q.filter(Project.status == status)
        else:
            q = q.filter(Project.status.in_(["planning", "active"]))
        projects = q.all()
        if not projects:
            return "当前没有符合条件的项目。"
        lines = [f"**项目列表** (共 {len(projects)} 个):"]
        for p in projects:
            lines.append(
                f"- [{p.source}] {p.name} | 负责人: {p.manager_name or '未指定'} | "
                f"状态: {p.status} | {p.start_date or '?'}-{p.end_date or '?'}"
            )
        return "\n".join(lines)
    finally:
        db.close()
