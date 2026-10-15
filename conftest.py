import os

# Must be set before main is imported, so the tests never create or read a real api_key.txt
os.environ["HEAT_API_KEY"] = "test-key"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import main

KEY = "test-key"


@pytest.fixture()
def raw():
    """A test client with an empty in-memory database and NO api key."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    main.Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    main.app.dependency_overrides[main.get_db] = override_get_db
    with TestClient(main.app) as c:
        yield c
    main.app.dependency_overrides.clear()


@pytest.fixture()
def client(raw):
    """The same test client, but sending the right api key."""
    raw.headers.update({"X-API-Key": KEY})
    return raw
