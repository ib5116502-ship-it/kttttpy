from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.models.booking import Booking
from src.models.room import Room
from src.models.user import User
from src.schemas.booking import BookingCreate
from src.tasks.notifications import send_booking_confirmation


def list_bookings(db: Session, current_user: User) -> list[Booking]:
    if current_user.role == "admin":
        return db.query(Booking).order_by(Booking.id.desc()).all()
    return db.query(Booking).filter(Booking.user_id == current_user.id).order_by(Booking.id.desc()).all()


def create_booking(db: Session, payload: BookingCreate, current_user: User) -> Booking:
    if payload.end_time <= payload.start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="end_time must be later than start_time",
        )

    room = db.query(Room).filter(Room.id == payload.room_id).first()
    if not room or not room.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found or inactive",
        )

    overlap = (
        db.query(Booking)
        .filter(
            Booking.room_id == room.id,
            Booking.status == "confirmed",
            Booking.start_time < payload.end_time,
            Booking.end_time > payload.start_time,
        )
        .first()
    )
    if overlap:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Room is already booked for this time interval",
        )

    booking = Booking(
        user_id=current_user.id,
        room_id=room.id,
        start_time=payload.start_time,
        end_time=payload.end_time,
        status="confirmed",
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)

    # Фоновая задача Celery: не падаем, если воркер/брокер недоступен в тестах
    try:
        send_booking_confirmation.delay(booking.id, current_user.email, room.name)
    except Exception as exc:
        print(f"[WARNING] Failed to enqueue Celery task: {exc}")

    return booking