from sqlalchemy import create_engine, Column, Integer, String, Text, Date, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
import enum

from src.config import config

engine = create_engine(config.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


class MemberStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"


class TaskStatus(str, enum.Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"


class ProjectSource(str, enum.Enum):
    internal = "internal"
    external = "external"


class EventType(str, enum.Enum):
    meeting = "meeting"
    visit = "visit"
    competition = "competition"
    lecture = "lecture"


class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    wx_userid = Column(String(100), nullable=True)
    department = Column(String(50), nullable=False)
    role = Column(String(50), nullable=False)
    phone = Column(String(20), nullable=True)
    join_date = Column(Date, nullable=True)
    status = Column(SAEnum(MemberStatus), default=MemberStatus.active)

    tasks = relationship("Task", back_populates="assignee")
    managed_projects = relationship("Project", back_populates="manager")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    assignee_id = Column(Integer, ForeignKey("members.id"), nullable=True)
    assignee_name = Column(String(50), nullable=True)
    department = Column(String(50), nullable=True)
    status = Column(SAEnum(TaskStatus), default=TaskStatus.todo)
    priority = Column(String(20), default="normal")
    deadline = Column(Date, nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    assignee = relationship("Member", back_populates="tasks")
    project = relationship("Project", back_populates="tasks")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    source = Column(SAEnum(ProjectSource), default=ProjectSource.internal)
    manager_id = Column(Integer, ForeignKey("members.id"), nullable=True)
    manager_name = Column(String(50), nullable=True)
    status = Column(String(30), default="planning")
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    result_summary = Column(Text, nullable=True)
    archive_url = Column(String(500), nullable=True)

    manager = relationship("Member", back_populates="managed_projects")
    tasks = relationship("Task", back_populates="project")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    type = Column(SAEnum(EventType), nullable=False)
    date = Column(Date, nullable=False)
    location = Column(String(200), nullable=True)
    participants = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    archive_url = Column(String(500), nullable=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
