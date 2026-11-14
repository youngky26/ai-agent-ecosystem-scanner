import os
from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, JSON, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy import create_engine

from .config import settings


class Base(DeclarativeBase):
    pass


class ScanRun(Base):
    __tablename__ = "scan_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    scanned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    count: Mapped[int] = mapped_column(Integer, default=0)
    repositories: Mapped[list] = mapped_column(JSON)


def build_engine(database_url: str):
    if database_url.startswith("sqlite:///"):
        path = database_url.removeprefix("sqlite:///")
        if path != ":memory:" and path.startswith("/"):
            os.makedirs(os.path.dirname(path), exist_ok=True)
        elif path != ":memory:":
            parent = os.path.dirname(path)
            if parent:
                os.makedirs(parent, exist_ok=True)
        return create_engine(
            database_url,
            connect_args={"check_same_thread": False} if path != ":memory:" else {},
        )
    return create_engine(database_url, pool_pre_ping=True)


engine = build_engine(settings.database_url)
Base.metadata.create_all(engine)


def save_scan(repositories: list[dict], scanned_at: datetime | None = None, db_engine=None) -> int:
    target_engine = db_engine or engine
    if db_engine is not None:
        Base.metadata.create_all(target_engine)
    factory = sessionmaker(bind=target_engine, expire_on_commit=False)
    with factory() as session:
        run = ScanRun(
            scanned_at=scanned_at or datetime.now(timezone.utc),
            count=len(repositories),
            repositories=repositories,
        )
        session.add(run)
        session.commit()
        session.refresh(run)
        return run.id


def latest_repositories(db_engine=None) -> list[dict]:
    factory = sessionmaker(bind=db_engine or engine)
    with factory() as session:
        run = session.scalar(
            select(ScanRun).order_by(ScanRun.scanned_at.desc(), ScanRun.id.desc()).limit(1)
        )
        return run.repositories if run else []


def list_scans(limit: int = 20, db_engine=None) -> list[dict]:
    factory = sessionmaker(bind=db_engine or engine)
    with factory() as session:
        runs = session.scalars(
            select(ScanRun).order_by(ScanRun.scanned_at.desc(), ScanRun.id.desc()).limit(limit)
        ).all()
        return [
            {"id": run.id, "scanned_at": run.scanned_at.isoformat(), "count": run.count}
            for run in runs
        ]


def get_scan(scan_id: int, db_engine=None) -> dict | None:
    factory = sessionmaker(bind=db_engine or engine)
    with factory() as session:
        run = session.get(ScanRun, scan_id)
        if not run:
            return None
        return {
            "id": run.id,
            "scanned_at": run.scanned_at.isoformat(),
            "count": run.count,
            "repositories": run.repositories,
        }
