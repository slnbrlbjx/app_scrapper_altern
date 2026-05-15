from fastapi import APIRouter
from sqlalchemy.orm import Session

from database.database import SessionLocal
from models.job import Job

router = APIRouter()


@router.get("/jobs")
def get_jobs():
    db: Session = SessionLocal()

    jobs = db.query(Job).order_by(Job.created_at.desc()).all()

    return jobs