import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from .db_models import metadata

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///unitron.db")
IS_SQLITE = DATABASE_URL.startswith("sqlite")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if IS_SQLITE else {},
    pool_pre_ping=not IS_SQLITE,
)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    with engine.begin() as conn:
        metadata.create_all(conn)

async def save_discovered_domains(domains: list[str]) -> None:
    if not domains:
        return
    init_db()
    with SessionLocal() as session:
        for d in domains:
            session.execute(
                text("INSERT OR IGNORE INTO discovered_domains(domain) VALUES(:d)"),
                {"d": d},
            )
        session.commit()

def list_discovered_domains(limit: int | None = None) -> list[str]:
    init_db()
    with SessionLocal() as session:
        query = "SELECT domain FROM discovered_domains ORDER BY discovered_at DESC"
        if limit:
            query += f" LIMIT {limit}"
        rows = session.execute(text(query)).all()
    return [r[0] for r in rows]

def upsert_job(job_id: str, stage: str, status: str, result_url: str | None = None) -> None:
    init_db()
    with SessionLocal() as session:
        session.execute(
            text(
                "INSERT INTO job_statuses(job_id, stage, status, result_url) VALUES(:id,:st,:stat,:url) "
                "ON CONFLICT(job_id) DO UPDATE SET stage=:st, status=:stat, result_url=:url"
            ),
            {"id": job_id, "st": stage, "stat": status, "url": result_url},
        )
        session.commit()

def get_job(job_id: str) -> dict | None:
    init_db()
    with SessionLocal() as session:
        row = session.execute(
            text("SELECT job_id, stage, status, result_url FROM job_statuses WHERE job_id=:id"),
            {"id": job_id},
        ).fetchone()
        if row:
            return {"job_id": row[0], "stage": row[1], "status": row[2], "result_url": row[3]}
        return None
