from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import threading

from . import crud, database, models, pika_client
from shared.app import schemas

app = FastAPI(title="Product Service")

@app.on_event("startup")
async def startup_event():
    database.init_db() # Create tables on startup
    # Start the RabbitMQ listener in a separate thread
    listener_thread = threading.Thread(target=pika_client.start_consuming, daemon=True)
    listener_thread.start()

@app.post("/products", response_model=schemas.Product, status_code=201)
def create_product(product: schemas.ProductCreate, db: Session = Depends(database.get_db)):
    return crud.create_product(db=db, product=product)

@app.get("/products/{product_id}", response_model=schemas.Product)
def read_product(product_id: int, db: Session = Depends(database.get_db)):
    db_product = crud.get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product