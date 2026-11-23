from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import get_current_user, require_role
from src.schemas.room import RoomCreate, RoomOut, RoomUpdate
from src.services.room_service import create_room, delete_room, get_room_or_404, list_rooms, update_room

router = APIRouter(prefix="/rooms", tags=["Rooms"])


@router.get("/", response_model=list[RoomOut])
def get_all_rooms(
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return list_rooms(db)


@router.get("/{room_id}", response_model=RoomOut)
def get_one_room(
    room_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return get_room_or_404(db, room_id)


@router.post("/", response_model=RoomOut, status_code=status.HTTP_201_CREATED)
def add_room(
    payload: RoomCreate,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
):
    return create_room(db, payload)


@router.patch("/{room_id}", response_model=RoomOut)
def patch_room(
    room_id: int,
    payload: RoomUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
):
    return update_room(db, room_id, payload)


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_room(
    room_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
):
    delete_room(db, room_id)