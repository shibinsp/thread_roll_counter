from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Database setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(os.path.dirname(BASE_DIR), 'thread_rolls.db')}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Record(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    image_filename = Column(String, nullable=False)
    total_count = Column(Integer, nullable=False)
    color_counts = Column(JSON, nullable=False)
    raw_detection = Column(JSON, nullable=False)
    description = Column(Text, nullable=True)
    user = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
