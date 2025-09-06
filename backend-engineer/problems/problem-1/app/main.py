from fastapi import FastAPI
from .database import engine
from . import models
from .routers import auth, projects_tasks

# This line creates the tables if they don't exist. 
# In a production app, you would use Alembic for this.
# models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Ragworks Task Management API",
    description="An API for managing projects and tasks.",
    version="1.0.0"
)

app.include_router(auth.router)
app.include_router(projects_tasks.router)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Task Management API"}