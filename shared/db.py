import os
import asyncpg
from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects import postgresql

from .db_models import metadata

_pool: asyncpg.Pool | None = None

async def get_pool() -> asyncpg.Pool:
    """Return a singleton connection pool."""
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            user=os.getenv("PGUSER", "presales"),
            password=os.getenv("PGPASSWORD", "password"),
            database=os.getenv("PGDATABASE", "presales"),
            host=os.getenv("PGHOST", "db"),
        )
    return _pool

async def init_db() -> None:
    """Create tables defined in ``db_models`` if they don't exist."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        for table in metadata.sorted_tables:
            ddl = str(CreateTable(table, if_not_exists=True).compile(dialect=postgresql.dialect()))
            await conn.execute(ddl)

async def save_discovered_domains(domains: list[str]) -> None:
    """Insert discovered domains, ignoring duplicates."""
    if not domains:
        return
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.executemany(
            "INSERT INTO discovered_domains(domain) VALUES($1) "
            "ON CONFLICT (domain) DO NOTHING",
            [(d,) for d in domains],
        )

async def upsert_job(job_id: str, stage: str, status: str, result_url: str | None = None) -> None:
    """Insert or update a job status record."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO job_statuses(job_id, stage, status, result_url) "
            "VALUES($1,$2,$3,$4) "
            "ON CONFLICT (job_id) DO UPDATE SET stage=EXCLUDED.stage, "
            "status=EXCLUDED.status, result_url=EXCLUDED.result_url",
            job_id,
            stage,
            status,
            result_url,
        )

async def get_job(job_id: str) -> dict | None:
    """Fetch a job status record by ID."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT job_id, stage, status, result_url FROM job_statuses WHERE job_id=$1",
            job_id,
        )
    return dict(row) if row else None

