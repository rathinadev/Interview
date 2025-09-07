
import json
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as aioredis
from . import crud, schemas
from .core.db import get_async_db, get_sync_db, get_redis_client

app = FastAPI(title="Performance Optimization Demo")

@app.get("/report/slow", response_model=schemas.ReportResponse)
def read_slow_report(category: str = "electronics", db: Session = Depends(get_sync_db)):
    report_data = crud.get_sales_report_slow_sync(db, category)
    return {"source": "database", "category": category, "report": report_data}

@app.get("/report/fast", response_model=schemas.ReportResponse)
async def read_fast_report(
    category: str = "electronics",
    db: AsyncSession = Depends(get_async_db),
    redis: aioredis.Redis = Depends(get_redis_client)
):
    cache_key = f"report:{category}"
    cached_report = await redis.get(cache_key)
    if cached_report:
        report_list = json.loads(cached_report)
        return {"source": "cache", "category": category, "report": report_list}

    report_data = await crud.get_sales_report_fast_async(db, category)
    report_list_for_cache = [
        {"name": row.name, "total_quantity": row.total_quantity} for row in report_data
    ]
    await redis.setex(cache_key, 300, json.dumps(report_list_for_cache))
    return {"source": "database", "category": category, "report": report_data}