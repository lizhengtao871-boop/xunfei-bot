from datetime import date
from src.agent.tool_registry import register_tool
from src.db.models import SessionLocal, Event


@register_tool(
    name="query_events",
    description="查询协会的活动和会议安排。可按类型和时间筛选。",
    parameters={
        "type": "object",
        "properties": {
            "event_type": {"type": "string", "enum": ["meeting", "visit", "competition", "lecture"]},
            "month": {"type": "string", "description": "月份，如 '2026-06'"},
        },
    },
)
def query_events(event_type: str | None = None, month: str | None = None) -> str:
    db = SessionLocal()
    try:
        q = db.query(Event).order_by(Event.date.desc())
        if event_type:
            q = q.filter(Event.type == event_type)
        if month:
            start = date.fromisoformat(month + "-01")
            end = date(start.year, start.month + 1, 1) if start.month < 12 else date(start.year + 1, 1, 1)
            q = q.filter(Event.date >= start, Event.date < end)
        else:
            q = q.filter(Event.date >= date.today()).order_by(Event.date.asc())
        events = q.limit(20).all()
        if not events:
            return "没有找到符合条件的活动。" + (f" ({month})" if month else "")
        lines = ["**活动列表**:"]
        for e in events:
            lines.append(f"- 📅 {e.date} | [{e.type}] {e.title} | 📍{e.location or '待定'}")
        return "\n".join(lines)
    finally:
        db.close()
