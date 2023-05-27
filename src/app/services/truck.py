from fastapi import Depends, HTTPException, status
from sqlalchemy import exists
from sqlalchemy.orm import Session

from app import tables
from app.db import get_session
from app.models.truck import TruckCreate, TruckUpdate


class TruckService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def _get(self, truck_id: int) -> tables.Truck:
        truck = (
            self.session.query(tables.Truck).filter(tables.Truck.id == truck_id).first()
        )
        if not truck:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Truck with id: {truck_id} not found",
            )
        return truck

    def get_list(self) -> list[tables.Truck]:
        return self.session.query(tables.Truck).all()

    def get(self, truck_id: int):
        return self._get(truck_id=truck_id)

    def create(self, truck_data: TruckCreate) -> tables.Truck:
        current_location_id = truck_data.current_location_id
        if not self.session.query(
            exists().where(tables.Location.zip == current_location_id)
        ).scalar():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="location does not exsists",
            )
        truck = tables.Truck(**truck_data.dict())
        self.session.add(truck)
        self.session.commit()
        return truck

    def update(self, truck_id: int, truck_data: TruckUpdate) -> tables.Truck:
        truck = self._get(truck_id=truck_id)
        location_id = truck_data.current_location_id
        if not self.session.query(
            exists().where(tables.Location.zip == location_id)
        ).scalar():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Location does not exist"
            )
        truck.name = truck_data.name
        truck.current_location_id = truck_data.current_location_id
        truck.truck_number = truck_data.truck_number
        truck.carrying_capacity = truck_data.carrying_capacity
        self.session.add(truck)
        self.session.commit()
        return truck

    def delete(self, truck_id: int):
        truck = self._get(truck_id)
        self.session.delete(truck)
        self.session.commit()
