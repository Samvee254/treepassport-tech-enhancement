import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_treepassport.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def field_officer_token(client):
    client.post("/auth/register", json={
        "name": "Test Officer",
        "email": "test_officer@example.com",
        "password": "testpass123",
        "role": "field_officer",
    })
    res = client.post("/auth/login", json={
        "email": "test_officer@example.com",
        "password": "testpass123",
    })
    return res.json()["access_token"]


@pytest.fixture
def viewer_token(client):
    client.post("/auth/register", json={
        "name": "Test Viewer",
        "email": "test_viewer@example.com",
        "password": "testpass123",
        "role": "viewer",
    })
    res = client.post("/auth/login", json={
        "email": "test_viewer@example.com",
        "password": "testpass123",
    })
    return res.json()["access_token"]
