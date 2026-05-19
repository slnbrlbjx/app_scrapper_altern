from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from database.database import get_db
from models.job import Job

router = APIRouter(prefix="/api")


@router.get("/jobs")
def get_jobs(
    db: Session = Depends(get_db),
    source: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    limit: int = Query(100, le=500),
    offset: int = Query(0),
):
    query = db.query(Job).order_by(Job.created_at.desc())

    if source:
        query = query.filter(Job.source == source)
    if keyword:
        kw = f"%{keyword.lower()}%"
        query = query.filter(
            Job.title.ilike(kw) | Job.description.ilike(kw) | Job.company.ilike(kw)
        )

    total = query.count()
    jobs = query.offset(offset).limit(limit).all()

    return {
        "total": total,
        "jobs": [
            {
                "id": j.id,
                "title": j.title,
                "company": j.company,
                "city": j.city,
                "region": j.region,
                "contract_type": j.contract_type,
                "source": j.source,
                "url": j.url,
                "description": j.description,
                "salary": j.salary,
                "remote_type": j.remote_type,
                "tags": j.tags,
                "posted_at": j.posted_at,
                "created_at": j.created_at,
            }
            for j in jobs
        ],
    }


@router.get("/sources")
def get_sources(db: Session = Depends(get_db)):
    sources = db.query(Job.source).distinct().all()
    return [s[0] for s in sources if s[0]]
