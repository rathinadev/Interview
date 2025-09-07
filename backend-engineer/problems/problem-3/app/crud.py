from sqlalchemy import func, select
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from . import models

# --- SLOW SYNCHRONOUS VERSION ---
# This simulates the original, unoptimized query.
def get_sales_report_slow_sync(db: Session, category: str):
    return db.query(
        models.Product.name,
        func.sum(models.Sale.quantity).label("total_quantity")
    ).join(models.Sale).where(
        models.Product.category == category
    ).group_by(models.Product.name).order_by(
        func.sum(models.Sale.quantity).desc()
    ).all()

# --- FAST ASYNCHRONOUS VERSION ---
# This query is identical but will be fast due to the index on `category`
# and runs asynchronously to not block the server.
async def get_sales_report_fast_async(db: AsyncSession, category: str):
    query = select(
        models.Product.name,
        func.sum(models.Sale.quantity).label("total_quantity")
    ).join(models.Sale).where(
        models.Product.category == category
    ).group_by(models.Product.name).order_by(
        func.sum(models.Sale.quantity).desc()
    )
    result = await db.execute(query)
    return result.all()