from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.core.database import Base, get_db
from src.main import app

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


Base.metadata.create_all(bind=engine)
app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_register_login_rbac_and_booking():
    admin_resp = client.post(
        "/auth/register",
        json={"email": "admin@example.com", "password": "secret123", "role": "admin"},
    )
    assert admin_resp.status_code in (200, 201)

    user_resp = client.post(
        "/auth/register",
        json={"email": "user@example.com", "password": "secret123", "role": "user"},
    )
    assert user_resp.status_code in (200, 201)

    admin_login = client.post(
        "/auth/login",
        data={"username": "admin@example.com", "password": "secret123"},
    )
    assert admin_login.status_code == 200
    admin_token = admin_login.json()["access_token"]

    user_login = client.post(
        "/auth/login",
        data={"username": "user@example.com", "password": "secret123"},
    )
    assert user_login.status_code == 200
    user_token = user_login.json()["access_token"]

    forbidden_room = client.post(
        "/rooms/",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"name": "Meeting Room A", "capacity": 10},
    )
    assert forbidden_room.status_code == 403

    created_room = client.post(
        "/rooms/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name": "Meeting Room A", "capacity": 10},
    )
    assert created_room.status_code in (200, 201)
    room_id = created_room.json()["id"]

    now = datetime.now(timezone.utc) + timedelta(hours=1)
    booking_resp = client.post(
        "/bookings/",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "room_id": room_id,
            "start_time": now.isoformat(),
            "end_time": (now + timedelta(hours=2)).isoformat(),
        },
    )
    assert booking_resp.status_code in (200, 201)
    assert booking_resp.json()["room_id"] == room_id