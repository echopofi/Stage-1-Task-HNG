import datetime
import uuid
from uuid6 import uuid7
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./profiles.db"
engine = create_engine(DATABASE_URL,
                       connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid7()))
    name = Column(String, unique=True, index=True, nullable=False)
    gender = Column(String)
    gender_probability = Column(Float)
    sample_size = Column(Integer)
    age = Column(Integer)
    age_group = Column(String)
    country_id = Column(String)
    country_probability = Column(Float)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

def init_db():
    Base.metadata.create_all(bind=engine)