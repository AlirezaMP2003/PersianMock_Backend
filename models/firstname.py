from sqlalchemy import Column, Integer, String
from db.database import Base

class FirstName(Base):
    __tablename__ = "first_name"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    gender = Column(String(10), unique=True, nullable=False)
