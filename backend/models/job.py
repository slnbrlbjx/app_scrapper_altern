from sqlalchemy import Column, Integer, Text, TIMESTAMP, Index
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql import func

from database.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=False)
    company = Column(Text)
    city = Column(Text)
    region = Column(Text)
    contract_type = Column(Text)
    source = Column(Text, index=True)
    url = Column(Text, unique=True, nullable=False)
    description = Column(Text)
    salary = Column(Text)
    remote_type = Column(Text)
    tags = Column(ARRAY(Text), default=[])
    posted_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, server_default=func.now(), index=True)

    __table_args__ = (
        Index("ix_jobs_source_created", "source", "created_at"),
    )
