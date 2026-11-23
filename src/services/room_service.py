from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.models.room import Room
from src.schemas.room import RoomCreate, RoomUpdate


def list_rooms(db: Session) -> list[Room]:
    return db.query(Room).order_by(Room.id).all()


def get_room_or_404(db: Session, room_id: int) -> Room:
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    return room


def create_room(db: Session, payload: RoomCreate) -> Room:
    existing = db.query(Room).filter(Room.name == payload.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room with this name already exists",
        )

    room = Room(**payload.model_dump())
    db.add(room)
    db.commit()
    db.refresh(room)
    return room


def update_room(db: Session, room_id: int, payload: RoomUpdate) -> Room:
    room = get_room_or_404(db, room_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(room, field, value)
    db.commit()
    db.refresh(room)
    return room


def delete_room(db: Session, room_id: int) -> None:
    room = get_room_or_404(db, room_id)
    db.delete(room)
    db.commit()