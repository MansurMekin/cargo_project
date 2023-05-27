from pydantic import BaseModel


class LocationBase(BaseModel):
    zip: str
    lat: str
    lng: str
    city: str
    state_name: str


class LocationCreate(LocationBase):
    pass


class Location(LocationBase):
    class Config:
        orm_mode = True
