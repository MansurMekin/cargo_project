from pydantic import BaseModel

from .location import Location


class TruckBase(BaseModel):
    name: str
    truck_number: str
    current_location_id: str
    carrying_capacity: float


class TruckCreate(TruckBase):
    pass


class TruckUpdate(TruckBase):
    pass


class Truck(TruckBase):
    id: int
    current_location: Location

    class Config:
        orm_mode = True
