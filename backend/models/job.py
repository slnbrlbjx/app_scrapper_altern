from sqlalchemy import Column, Integer, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql import func

from database.database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text)
    company = Column(Text)
    city = Column(Text)
    region = Column(Text)
    contract_type = Column(Text)
    source = Column(Text)
    url = Column(Text, unique=True)
    description = Column(Text)
    salary = Column(Text)
    remote_type = Column(Text)
    tags = Column(ARRAY(Text))
    posted_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, server_default=func.now())