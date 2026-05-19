from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError
import os
import time

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@db:5432/jobs"
)

# Retry logic for DB connection at startup
for attempt in range(10):
    try:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        engine.connect()
        break
    except OperationalError:
        if attempt == 9:
            raise
        time.sleep(2)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    """FastAPI dependency for DB sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def save_jobs(jobs: list[dict], source: str):
    """Upsert jobs into DB, skip duplicates by URL."""
    from models.job import Job
    db = SessionLocal()
    new_count = 0
    try:
        for job_data in jobs:
            url = job_data.get("url", "")
            if not url:
                continue
            existing = db.query(Job).filter(Job.url == url).first()
            if existing:
                continue
            job = Job(
                title=job_data.get("title", ""),
                company=job_data.get("company", ""),
                city=job_data.get("city", ""),
                region=job_data.get("region", ""),
                contract_type=job_data.get("contract_type", ""),
                source=source,
                url=url,
                description=job_data.get("description", ""),
                salary=job_data.get("salary", ""),
                remote_type=job_data.get("remote_type", ""),
                tags=job_data.get("tags", []),
                posted_at=job_data.get("posted_at"),
            )
            db.add(job)
            new_count += 1
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
    return new_count
