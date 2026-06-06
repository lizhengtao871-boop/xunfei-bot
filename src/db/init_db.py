from datetime import date
from src.db.models import engine, Base, SessionLocal, Member, MemberStatus

SEED_MEMBERS = [
    {"name": "会长", "department": "会长团", "role": "会长", "status": MemberStatus.active},
    {"name": "副会长(宣传)", "department": "会长团", "role": "副会长", "status": MemberStatus.active},
    {"name": "副会长(资源)", "department": "会长团", "role": "副会长", "status": MemberStatus.active},
]


def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Member).count() == 0:
            for m in SEED_MEMBERS:
                db.add(Member(
                    name=m["name"],
                    department=m["department"],
                    role=m["role"],
                    status=m["status"],
                    join_date=date.today(),
                ))
            db.commit()
            print(f"Seeded {len(SEED_MEMBERS)} initial members.")
        else:
            print("Database already initialized, skipping seed.")
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
