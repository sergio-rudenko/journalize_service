from fastapi import FastAPI

from app.api.crud_types import router as crud_types_router
from app.api.crud_devices import router as crud_devices_router

from app.db import metadata, database, engine

metadata.create_all(engine)

app = FastAPI(
    version="0.0.1",
    title="Journalize",
    description="Service to store data from MQTT device topic to Postgres database"
)


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


# test routes
@app.get("/", tags=["test"])
def get_root():
    return {"result": "Hello, World!"}


@app.get("/items/{item_id}", tags=["test"])
def get_item(item_id: int, q: str = None):
    return {"id": item_id, "q": q}


app.include_router(crud_types_router, prefix='/types', tags=["CRUD Device types"])
app.include_router(crud_devices_router, prefix='/devices', tags=["CRUD Devices"])
