from datetime import date
from src.agent.tool_registry import register_tool
from src.db.models import SessionLocal, Task, Project, Event


@register_tool(
    name="generate_report",
    description="生成协会阶段性汇报，汇总项目进展、任务完成情况和活动记录。",
    parameters={
        "type": "object",
        "properties": {
            "period": {"type": "string", "description": "汇报周期，如 '本月'、'本学期'、'2026年5月'"},
        },
        "required": ["period"],
    },
)
def generate_report(period: str = "本月") -> str:
    db = SessionLocal()
    try:
        today = date.today()
        start = today.replace(day=1)

        projects = db.query(Project).all()
        tasks_done = db.query(Task).filter(Task.status == "done").count()
        tasks_total = db.query(Task).count()
        events = db.query(Event).filter(Event.date >= start, Event.date <= today).all()

        lines = [
            f"**讯飞人工智能协会 {period} 汇报**",
            "",
            "## 项目进展",
        ]
        for p in projects:
            task_count = db.query(Task).filter(Task.project_id == p.id).count() if p.id else 0
            done_count = db.query(Task).filter(Task.project_id == p.id, Task.status == "done").count() if p.id else 0
            lines.append(f"- **{p.name}** [{p.source}] | 状态: {p.status} | 任务: {done_count}/{task_count}")

        lines.extend([
            "",
            "## 任务概览",
            f"- 总任务: {tasks_total}, 已完成: {tasks_done}",
            "",
            "## 近期活动",
        ])
        if events:
            for e in events:
                lines.append(f"- {e.date} [{e.type}] {e.title}")
        else:
            lines.append("暂无活动记录。")

        lines.extend([
            "",
            "## 关键成果",
            "（请补充本阶段的关键成果和亮点）",
        ])
        return "\n".join(lines)
    finally:
        db.close()
