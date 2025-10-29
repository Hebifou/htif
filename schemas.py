from pydantic import BaseModel
from typing import List, Optional

class AnalyzeRequest(BaseModel):
    topic: str = "klima"
    social_platform: Optional[str] = None
    social_id: Optional[str] = None
    comment_limit: int = 100

class AnalyzeResult(BaseModel):
    message: str
    record_count: int
    csv_url: str
    data: List[dict]
