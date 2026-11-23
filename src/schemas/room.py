from pydantic import BaseModel, ConfigDict, Field


class RoomCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    capacity: int = Field(ge=1, le=500)
    is_active: bool = True


class RoomUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    capacity: int | None = Field(default=None, ge=1, le=500)
    is_active: bool | None = None


class RoomOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    capacity: int
    is_active: bool