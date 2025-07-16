import os, asyncpg

async def get_pool():
    return await asyncpg.create_pool(
        user=os.getenv("PGUSER", "presales"),
        password=os.getenv("PGPASSWORD", "password"),
        database=os.getenv("PGDATABASE", "presales"),
        host=os.getenv("PGHOST", "db"),
    )
