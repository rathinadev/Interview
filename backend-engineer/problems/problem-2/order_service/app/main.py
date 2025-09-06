from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy.orm import Session
import httpx

from . import crud, database, models, pika_client
from shared.app import schemas, settings

app = FastAPI(title="Order Service")

@app.on_event("startup")
def on_startup():
    database.init_db()

settings_obj = settings.Settings()

@app.post("/orders", response_model=schemas.Order, status_code=201)
async def create_order(order: schemas.OrderCreate, user_id: int = Header(...), db: Session = Depends(database.get_db)):
    total_price = 0.0
    
    async with httpx.AsyncClient() as client:
        for item in order.items:
            try:
                response = await client.get(f"{settings_obj.PRODUCT_SERVICE_URL}/products/{item.product_id}")
                response.raise_for_status()
                product = response.json()

                if product['quantity'] < item.quantity:
                    raise HTTPException(status_code=400, detail=f"Not enough stock for product ID {item.product_id}")
                
                total_price += product['price'] * item.quantity
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    raise HTTPException(status_code=404, detail=f"Product with ID {item.product_id} not found")
                else:
                    raise HTTPException(status_code=500, detail="Product service is unavailable")

    db_order = crud.create_order(db, user_id=user_id, total_price=total_price)
    
    # Publish event to RabbitMQ for inventory update
    pika_client.publish_order_created(db_order.id, order.items)
    
    # Enrich the response with items for clarity
    response_order = schemas.Order.from_orm(db_order)
    response_order.items = order.items
    
    return response_order