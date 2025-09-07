from pydantic import BaseModel
from typing import List

class ReportItem(BaseModel):
    name: str
    total_quantity: int

    class Config:
        from_attributes = True

class ReportResponse(BaseModel):
    source: str
    category: str
    report: List[ReportItem]