from datetime import date
from src.db.models import engine, Base, SessionLocal, Member, MemberStatus

SEED_MEMBERS = [
    {"name": "李正涛", "department": "外联部", "role": "副部长"},
    {"name": "刘月", "department": "主席团", "role": "副会长"},
    {"name": "刘美玲", "department": "主席团", "role": "副会长"},
    {"name": "易子雅", "department": "技术部", "role": "部长"},
    {"name": "吴安迪", "department": "技术部", "role": "副部长"},
    {"name": "杨振霖", "department": "技术部", "role": "副部长"},
    {"name": "刘锦翔", "department": "技术部", "role": "副部长"},
    {"name": "吕少锡", "department": "组织部", "role": "部长"},
    {"name": "张馨月", "department": "组织部", "role": "副部长"},
    {"name": "熊雅岚", "department": "组织部", "role": "副部长"},
    {"name": "刘雅婷", "department": "宣传部", "role": "部长"},
    {"name": "李思思", "department": "宣传部", "role": "副部长"},
    {"name": "张莎玉", "department": "宣传部", "role": "副部长"},
    {"name": "李雅铃", "department": "财务部", "role": "部长"},
    {"name": "王雅琴", "department": "财务部", "role": "副部长"},
    {"name": "赖博", "department": "财务部", "role": "副部长"},
    {"name": "苏睿博", "department": "外联部", "role": "部长"},
    {"name": "况依茹", "department": "外联部", "role": "副部长"},
    {"name": "梁嘉龙", "department": "外联部", "role": "副部长"},
    {"name": "蒋峰", "department": "主席团", "role": "会长"},
    {"name": "文天能", "department": "主席团", "role": "副会长"},
    {"name": "杨雅雯", "department": "主席团", "role": "副会长"},
    {"name": "康家宁", "department": "技术部", "role": "部长"},
    {"name": "梁佳欣", "department": "技术部", "role": "副部长"},
    {"name": "康玙", "department": "技术部", "role": "副部长"},
    {"name": "张旭彬", "department": "技术部", "role": "副部长"},
    {"name": "向雅瑞", "department": "组织部", "role": "部长"},
    {"name": "张宁", "department": "组织部", "role": "副部长"},
    {"name": "周奕扬", "department": "组织部", "role": "副部长"},
    {"name": "刘星宇", "department": "组织部", "role": "副部长"},
    {"name": "陈慧媛", "department": "宣传部", "role": "部长"},
    {"name": "余奇龙", "department": "宣传部", "role": "副部长"},
    {"name": "王昕睿", "department": "宣传部", "role": "副部长"},
    {"name": "叶明珠", "department": "财务部", "role": "部长"},
    {"name": "张宇前", "department": "财务部", "role": "副部长"},
    {"name": "范婉婧", "department": "财务部", "role": "副部长"},
    {"name": "唐娜", "department": "外联部", "role": "部长"},
    {"name": "杨泽", "department": "外联部", "role": "副部长"},
    {"name": "吕欣月", "department": "外联部", "role": "副部长"},
]


def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Member).count() < len(SEED_MEMBERS):
            # Clear old seed data and re-import
            db.query(Member).delete()
            for m in SEED_MEMBERS:
                db.add(Member(
                    name=m["name"],
                    department=m["department"],
                    role=m["role"],
                    status=MemberStatus.active,
                    join_date=date.today(),
                ))
            db.commit()
            print(f"Seeded {len(SEED_MEMBERS)} members.")
        else:
            print(f"Database has {db.query(Member).count()} members, skipping seed.")
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
