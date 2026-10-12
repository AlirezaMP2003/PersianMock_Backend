
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from db.database import Base


class Car(Base):
    __tablename__ = "car"

    id = Column(Integer, primary_key=True, index=True)
    company = Column(String(100), nullable=False)
    name = Column(String(100), nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "company",
            "name",
            name="uq_car_company_name",
        ),
    )


class Province(Base):
    __tablename__ = "province"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)

    cities = relationship(
        "City",
        back_populates="province",
    )


class City(Base):
    __tablename__ = "city"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)

    province_id = Column(
        Integer,
        ForeignKey("province.id"),
        nullable=False,
        index=True,
    )

    province = relationship(
        "Province",
        back_populates="cities",
    )

    __table_args__ = (
        UniqueConstraint(
            "province_id",
            "name",
            name="uq_city_province_name",
        ),
    )
