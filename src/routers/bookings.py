from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import get_current_user
from src.models.user import User
from src.schemas.booking import BookingCreate, BookingOut
from src.services.booking_service import create_booking, list_bookings

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.get("/", response_model=list[BookingOut])
def get_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_bookings(db, current_user)


@router.post("/", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
def add_booking(
    payload: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_booking(db, payload, current_user)