from fastapi import FastAPI

from app.api import cargo, trucks
from app.db import SessionLocal
from app.tables import create_tables

app = FastAPI(
    title='Cargo app'
)


@app.on_event("startup")
async def startup_event():
    session = SessionLocal()
    try:
        await create_tables()
    finally:
        session.close()


app.include_router(trucks.router)
app.include_router(cargo.router)
