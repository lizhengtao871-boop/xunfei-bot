from src.agent.tool_registry import register_tool
from src.db.models import SessionLocal, Member


@register_tool(
    name="query_members",
    description="按部门或角色查询协会成员列表。",
    parameters={
        "type": "object",
        "properties": {
            "department": {"type": "string", "description": "部门名称，如'技术部'；不填则查全部"},
        },
    },
)
def query_members(department: str | None = None) -> str:
    db = SessionLocal()
    try:
        q = db.query(Member).filter(Member.status == "active")
        if department:
            q = q.filter(Member.department == department)
        members = q.all()
        if not members:
            return f"未找到{'部门为' + department + '的' if department else ''}活跃成员。"
        lines = [f"共 {len(members)} 人:"]
        for m in members:
            lines.append(f"- {m.name} | {m.department} | {m.role} | {m.phone or '无电话'}")
        return "\n".join(lines)
    finally:
        db.close()
