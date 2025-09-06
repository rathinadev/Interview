from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from shared.app.settings import Settings
from . import models

settings = Settings()
# Add pool_pre_ping to handle connection drops
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
