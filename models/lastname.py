from sqlalchemy import Column, Integer, String
from db.database import Base

class LastName(Base):
    __tablename__ = "last_name"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
