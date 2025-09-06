from sqlalchemy.orm import Session
from . import models
from shared.app import schemas

def get_product(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()

def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def decrease_product_quantity(db: Session, product_id: int, quantity_to_decrease: int):

    db_product = db.query(models.Product).filter(models.Product.id == product_id).with_for_update().first()
    
    if db_product and db_product.quantity >= quantity_to_decrease:
        db_product.quantity -= quantity_to_decrease
        db.commit()
    elif db_product:
        db.rollback()
        # In a real app, you would log this error or send a failure event.
        print(f"ERROR: Not enough stock for product ID {product_id}.")
    else:
        db.rollback()
        print(f"ERROR: Product with ID {product_id} not found for inventory update.")