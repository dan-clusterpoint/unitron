from pydantic import BaseModel

class JobStatus(BaseModel):
    job_id: str
    stage: str
    status: str        # pending | done | error
    result_url: str | None = None
