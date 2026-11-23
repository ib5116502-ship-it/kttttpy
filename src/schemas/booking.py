from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BookingCreate(BaseModel):
    room_id: int
    start_time: datetime
    end_time: datetime


class BookingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    room_id: int
    start_time: datetime
    end_time: datetime
    status: str
    created_at: datetime