from pydantic import BaseModel


class CargoBase(BaseModel):
    pick_up_location_id: str
    delivery_location_id: str
    weight: float
    description: str


class CargoCreate(CargoBase):
    pass


class CargoUpdate(BaseModel):
    weight: float
    description: str


class Cargo(CargoBase):
    id: int

    class Config:
        orm_mode = True
