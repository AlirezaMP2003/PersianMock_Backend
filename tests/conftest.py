import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from db.database import Base, get_db
from models import (
    FirstName,
    LastName,
    Car,
    Province,
    City,
)
from routers import generate, fields


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    TestingSession = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )

    Base.metadata.create_all(bind=engine)

    with TestingSession() as db:
        province = Province(name="تهران")
        db.add(province)
        db.flush()

        db.add_all([
            FirstName(
                name="علی",
                username="ali",
                email="ali@example.com",
                gender="male",
            ),
            LastName(name="احمدی"),
            City(
                name="کرج تست",
                province_id=province.id,
            ),
            Car(
                company="ایران‌خودرو",
                name="دنا",
            ),
        ])

        db.commit()

    app = FastAPI()

    app.include_router(
        generate.router,
        prefix="/generate",
    )

    app.include_router(
        fields.router,
        prefix="/fields",
    )

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
