from datetime import date
from src.agent.tool_registry import register_tool
from src.db.models import SessionLocal, Task, TaskStatus


@register_tool(
    name="task_crud",
    description="任务的创建、查询、更新状态。创建前需要确认。",
    parameters={
        "type": "object",
        "properties": {
            "action": {"type": "string", "enum": ["list", "create", "update_status"]},
            "title": {"type": "string", "description": "任务标题(create时必填)"},
            "description": {"type": "string", "description": "任务描述"},
            "assignee_name": {"type": "string", "description": "负责人姓名"},
            "department": {"type": "string", "description": "负责部门"},
            "deadline": {"type": "string", "description": "截止日期 YYYY-MM-DD"},
            "project_name": {"type": "string", "description": "所属项目名称"},
            "task_id": {"type": "integer", "description": "任务ID(update_status时必填)"},
            "status": {"type": "string", "enum": ["todo", "in_progress", "done"]},
        },
        "required": ["action"],
    },
)
def task_crud(
    action: str,
    title: str | None = None,
    description: str | None = None,
    assignee_name: str | None = None,
    department: str | None = None,
    deadline: str | None = None,
    project_name: str | None = None,
    task_id: int | None = None,
    status: str | None = None,
) -> str:
    db = SessionLocal()
    try:
        if action == "list":
            tasks = db.query(Task).filter(Task.status != "done").order_by(Task.deadline.asc()).limit(20).all()
            if not tasks:
                return "当前没有待处理的任务。"
            lines = ["**待处理任务**:"]
            for t in tasks:
                dl = t.deadline.isoformat() if t.deadline else "无截止"
                lines.append(f"- [{t.id}] {t.title} | {t.assignee_name or '未分配'} | {t.status} | ⏰{dl}")
            return "\n".join(lines)

        if action == "create":
            if not title:
                return "错误：创建任务需要提供 title。"
            task = Task(
                title=title,
                description=description or "",
                assignee_name=assignee_name,
                department=department,
                deadline=date.fromisoformat(deadline) if deadline else None,
            )
            db.add(task)
            db.commit()
            return f"任务已创建: [{task.id}] {task.title}"

        if action == "update_status":
            if not task_id or not status:
                return "错误：需要 task_id 和 status。"
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task:
                return f"未找到任务 ID={task_id}"
            task.status = status
            db.commit()
            return f"任务 [{task.id}] {task.title} 状态已更新为 {status}"

        return "未知操作。支持: list, create, update_status"
    finally:
        db.close()
