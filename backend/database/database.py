import logging
import os
import time

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import declarative_base, sessionmaker

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/jobs")

for attempt in range(10):
    try:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=5, max_overflow=10)
        engine.connect().close()
        break
    except OperationalError:
        if attempt == 9:
            raise
        logger.info("DB not ready, retrying in 2s... (%d/10)", attempt + 1)
        time.sleep(2)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def save_jobs(jobs: list[dict], source: str) -> list[dict]:
    """Upsert jobs by URL. Returns the list of dicts that were actually inserted."""
    from models.job import Job

    if not jobs:
        return []

    db = SessionLocal()
    inserted: list[dict] = []
    try:
        urls = [j.get("url") for j in jobs if j.get("url")]
        existing_urls = {
            row[0]
            for row in db.query(Job.url).filter(Job.url.in_(urls)).all()
        }
        for job_data in jobs:
            url = job_data.get("url", "")
            if not url or url in existing_urls:
                continue
            db.add(Job(
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
            ))
            inserted.append(job_data)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
    return inserted
