from sqlalchemy import MetaData, Table, Column, String, DateTime, Text, func

metadata = MetaData()

discovered_domains = Table(
    "discovered_domains",
    metadata,
    Column("domain", String, primary_key=True),
    Column("discovered_at", DateTime, server_default=func.now()),
)

job_statuses = Table(
    "job_statuses",
    metadata,
    Column("job_id", String, primary_key=True),
    Column("stage", String, nullable=False),
    Column("status", String, nullable=False),
    Column("result_url", Text),
)

