from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from src.db.models import SessionLocal, Member, Task, Project, Event

router = APIRouter(prefix="/admin", tags=["管理面板"])

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>讯飞协会 - 管理面板</title>
<style>
body { font-family: -apple-system, sans-serif; max-width: 900px; margin: 0 auto; padding: 2rem; background: #f5f5f5; }
.card { background: white; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,.1); }
h1 { color: #1a1a2e; } h2 { color: #16213e; font-size: 1.1rem; margin-top: 0; }
.stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; }
.stat { text-align: center; padding: 1rem; background: #f8f9fa; border-radius: 8px; }
.stat .num { font-size: 2rem; font-weight: bold; color: #0066cc; }
table { width: 100%%; border-collapse: collapse; }
th, td { text-align: left; padding: 8px 12px; border-bottom: 1px solid #eee; }
th { font-weight: 600; color: #666; font-size: .9rem; }
</style>
</head>
<body>
<h1>讯飞人工智能协会 管理面板</h1>
<div class="stats">%s</div>
<div class="card"><h2>任务概览</h2><table><tr><th>ID</th><th>标题</th><th>负责人</th><th>状态</th><th>截止</th></tr>%s</table></div>
<div class="card"><h2>项目列表</h2><table><tr><th>名称</th><th>来源</th><th>负责人</th><th>状态</th></tr>%s</table></div>
<div class="card"><h2>近期活动</h2><table><tr><th>日期</th><th>类型</th><th>标题</th><th>地点</th></tr>%s</table></div>
</body>
</html>"""


@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    db = SessionLocal()
    try:
        members_count = db.query(Member).filter(Member.status == "active").count()
        tasks_count = db.query(Task).filter(Task.status != "done").count()
        projects_count = db.query(Project).filter(Project.status.in_(["planning", "active"])).count()
        events_count = db.query(Event).count()

        stats = f"""
        <div class="stat"><div class="num">{members_count}</div>成员</div>
        <div class="stat"><div class="num">{tasks_count}</div>待处理任务</div>
        <div class="stat"><div class="num">{projects_count}</div>进行中项目</div>
        <div class="stat"><div class="num">{events_count}</div>活动记录</div>
        """

        tasks = db.query(Task).order_by(Task.deadline.asc()).limit(10).all()
        tasks_rows = "".join(
            f"<tr><td>{t.id}</td><td>{t.title}</td><td>{t.assignee_name or '-'}</td><td>{t.status}</td><td>{t.deadline or '-'}</td></tr>"
            for t in tasks
        ) or '<tr><td colspan="5">暂无任务</td></tr>'

        projects = db.query(Project).all()
        proj_rows = "".join(
            f"<tr><td>{p.name}</td><td>{p.source}</td><td>{p.manager_name or '-'}</td><td>{p.status}</td></tr>"
            for p in projects
        ) or '<tr><td colspan="4">暂无项目</td></tr>'

        events = db.query(Event).order_by(Event.date.desc()).limit(5).all()
        event_rows = "".join(
            f"<tr><td>{e.date}</td><td>{e.type}</td><td>{e.title}</td><td>{e.location or '-'}</td></tr>"
            for e in events
        ) or '<tr><td colspan="4">暂无活动</td></tr>'

        return DASHBOARD_HTML % (stats, tasks_rows, proj_rows, event_rows)
    finally:
        db.close()
