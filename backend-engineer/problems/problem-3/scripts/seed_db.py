
import random
from faker import Faker
from app.core.db import sync_engine, SyncSessionLocal
from app.models import Base, Product, Sale

def seed_database():
    session = SyncSessionLocal()
    fake = Faker()

    print("--- Dropping all tables... ---")
    Base.metadata.drop_all(sync_engine)
    print("--- Creating all tables... ---")
    Base.metadata.create_all(sync_engine)

    print("--- Seeding products... ---")
    product_categories = ["electronics", "books", "home goods", "toys", "clothing"]
    products = []
    for _ in range(10000):
        product = Product(
            name=fake.unique.bs().capitalize(),
            category=random.choice(product_categories)
        )
        products.append(product)
    session.bulk_save_objects(products)
    session.commit()
    print("✓ 10,000 Products seeded.")

    print("--- Seeding sales... (This will take a moment) ---")
    product_ids = [p[0] for p in session.query(Product.id).all()]
    
    sales_batch = []
    for i in range(200_000):
        sale = Sale(
            product_id=random.choice(product_ids),
            quantity=random.randint(1, 5),
            sale_date=fake.date_time_between(start_date="-1y", end_date="now")
        )
        sales_batch.append(sale)
        
        if len(sales_batch) >= 10000:
            session.bulk_save_objects(sales_batch)
            session.commit()
            sales_batch = []
            print(f"  ... {i+1} sales committed", end='\r')

    if sales_batch:
        session.bulk_save_objects(sales_batch)
        session.commit()
    
    print("\n✓ 200,000 Sales seeded.")
    print("--- Database seeding complete! ---")
    session.close()

if __name__ == "__main__":
    seed_database()