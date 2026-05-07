import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./dev.db")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class RadioStation(Base):
    __tablename__ = "radio_stations"
    id            = Column(Integer, primary_key=True, index=True)
    nama_stasiun  = Column(String, nullable=False)
    frekuensi_mhz = Column(Float,  nullable=False)
    kota          = Column(String, nullable=False)
    provinsi      = Column(String, nullable=False)
    format_musik  = Column(String, nullable=True)
    created_at    = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Tabel database berhasil dibuat")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()