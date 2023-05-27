from fastapi import APIRouter, Depends, Response, status

from app.models.cargo import Cargo, CargoCreate, CargoUpdate
from app.services.cargo import CargoService

router = APIRouter(tags=["cargos"], prefix="/cargos")


@router.get("/")
async def get_cargos(service: CargoService = Depends()):
    return service.get_list()


@router.get("/{cargo_id}")
async def get_cargo(cargo_id: int, service: CargoService = Depends()):
    return service.get(cargo_id=cargo_id)


@router.post("/create", response_model=Cargo)
async def create_cargo(cargo_data: CargoCreate, service: CargoService = Depends()):
    return service.create(cargo_data=cargo_data)


@router.put("/{cargo_id}", response_model=Cargo)
async def update_cargo(
    cargo_id: int, cargo_data: CargoUpdate, service: CargoService = Depends()
):
    return service.update(cargo_id=cargo_id, cargo_data=cargo_data)


@router.delete("/{cargo_id}")
async def delete_cargo(cargo_id: int, service: CargoService = Depends()):
    service.delete(cargo_id=cargo_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
