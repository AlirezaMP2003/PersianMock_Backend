from sqlalchemy import Column, Integer, String, Enum
from db.database import Base
import enum

class GenderEnum(enum.Enum):
    male = "male"
    female = "female"

class FirstName(Base):
    __tablename__ = "first_name"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    gender = Column(Enum(GenderEnum), nullable=False)
