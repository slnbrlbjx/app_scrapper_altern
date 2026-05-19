import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.database import Base, engine
from api.routes.jobs import router as jobs_router

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Alternance Cyber Scraper", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs_router)


@app.get("/")
def root():
    return {"status": "running", "version": "2.0.0"}
