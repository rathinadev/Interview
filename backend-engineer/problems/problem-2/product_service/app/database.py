from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from shared.app.settings import Settings
from . import models

settings = Settings()
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    # This will create all tables for the models registered with Base
    models.Base.metadata.create_all(bind=engine)