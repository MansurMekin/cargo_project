from fastapi import APIRouter, Depends, Response, status

from app.models.truck import Truck, TruckCreate, TruckUpdate
from app.services.truck import TruckService

router = APIRouter(tags=["trucks"], prefix="/trucks")


@router.get("/", response_model=list[Truck])
async def get_list(service: TruckService = Depends()):
    return service.get_list()


@router.get("/{truck_id}", response_model=Truck)
async def get_one(truck_id: int, service: TruckService = Depends()):
    return service.get(truck_id=truck_id)


@router.post("/create", response_model=Truck)
async def create_truck(truck_data: TruckCreate, service: TruckService = Depends()):
    return service.create(truck_data=truck_data)


@router.put("/{truck_id}", response_model=Truck)
async def update_truck(
    truck_id: int, truck_data: TruckUpdate, service: TruckService = Depends()
):
    return service.update(truck_id=truck_id, truck_data=truck_data)


@router.delete("/{truck_id}")
async def delete_cargo(truck_id: int, service: TruckService = Depends()):
    service.delete(truck_id=truck_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
