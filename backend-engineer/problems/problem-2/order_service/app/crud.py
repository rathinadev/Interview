from sqlalchemy.orm import Session
from . import models

def create_order(db: Session, user_id: int, total_price: float):
    db_order = models.Order(user_id=user_id, total_price=total_price)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order