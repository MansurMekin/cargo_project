from fastapi import Depends, HTTPException, status
from geopy import distance
from sqlalchemy import exists
from sqlalchemy.orm import Session

from app import tables
from app.db import get_session
from app.models.cargo import CargoCreate, CargoUpdate


def get_location_data(location):
    return {
        "zip": location.zip,
        "lat": location.lat,
        "lng": location.lng,
        "city": location.city,
        "state_name": location.state_name,
    }


class CargoService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def _get(self, cargo_id: int):
        cargo = (
            self.session.query(tables.Cargo).filter(tables.Cargo.id == cargo_id).first()
        )
        if not cargo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cargo with id: {cargo_id} not found",
            )
        return cargo

    def get_list(self):
        results = []
        cargos = self.session.query(tables.Cargo).all()
        trucks = self.session.query(tables.Truck).all()
        if cargos:
            for cargo in cargos:
                nearest_trucks_count = 0
                pick_up_location = cargo.pick_up_location
                delivery_location = cargo.delivery_location

                for truck in trucks:
                    truck_cargo_distance = distance.distance(
                        (truck.current_location.lat, truck.current_location.lng),
                        (pick_up_location.lat, pick_up_location.lng),
                    ).miles

                    if 0 <= truck_cargo_distance <= 450:
                        nearest_trucks_count += 1

                cargo_data = {
                    "id": cargo.id,
                    "pick_up_location": get_location_data(pick_up_location),
                    "delivery_location": get_location_data(delivery_location),
                    "distance_between_pick_up_to_delivery": cargo.calculate_distance(),
                    "nearest_trucks_count": nearest_trucks_count,
                }

                results.append(cargo_data)

        return results

    def get(self, cargo_id: int):
        cargo = self._get(cargo_id)
        trucks = self.session.query(tables.Truck).all()
        cargo_data = {
            "id": cargo.id,
            "pick_up_location": get_location_data(cargo.pick_up_location),
            "delivery_location": get_location_data(cargo.delivery_location),
            "weight": cargo.weight,
            "description": cargo.description,
            "trucks": [],
        }

        for truck in trucks:
            truck_location = (truck.current_location.lat, truck.current_location.lng)
            pick_up_location = (cargo.pick_up_location.lat, cargo.pick_up_location.lng)
            delivery_location = (
                cargo.delivery_location.lat,
                cargo.delivery_location.lng,
            )

            distance_to_pick_up = distance.distance(
                truck_location, pick_up_location
            ).miles
            distance_to_delivery = distance.distance(
                truck_location, delivery_location
            ).miles

            truck_info = {
                "number": truck.truck_number,
                "distance_to_pick_up": distance_to_pick_up,
                "distance_to_delivery": distance_to_delivery,
            }

            cargo_data["trucks"].append(truck_info)

        return cargo_data

    def create(self, cargo_data: CargoCreate):
        pick_up_location_id = cargo_data.pick_up_location_id
        delivery_location_id = cargo_data.delivery_location_id
        if (
            not self.session.query(
                exists().where(tables.Location.zip == pick_up_location_id)
            ).scalar()
            or not self.session.query(
                exists().where(tables.Location.zip == delivery_location_id)
            ).scalar()
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="location does not exsists",
            )
        cargo = tables.Cargo(**cargo_data.dict())
        self.session.add(cargo)
        self.session.commit()
        return cargo

    def update(self, cargo_id: int, cargo_data: CargoUpdate):
        cargo = self._get(cargo_id)
        for field, value in cargo_data:
            setattr(cargo, field, value)
        self.session.add(cargo)
        self.session.commit()
        return cargo

    def delete(self, cargo_id: int):
        cargo = self._get(cargo_id)
        self.session.delete(cargo)
        self.session.commit()
