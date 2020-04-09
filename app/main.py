from fastapi import FastAPI

from app.api.crud_device_types import router as crud_types_router
from app.api.crud_devices import router as crud_devices_router
from app.api.crud_journal import router as crud_journal
from app.api.gate_mqtt import router as gate_mqtt

from app.config import api_version, api_prefix, types_path, devices_path, journal_path, mqtt_path

from app.db import metadata, database, engine
from app.mqtt import mqtt_connect, mqtt_disconnect

metadata.create_all(engine)



app = FastAPI(
    version="0.0.1",
    title="Journalize",
    description="Service to store data from MQTT device topic to Postgres database",
    redoc_url=f'{api_prefix}/redoc',
    docs_url=f'{api_prefix}/docs'
)


@app.on_event("startup")
async def startup():
    await database.connect()
    mqtt_connect()


@app.on_event("shutdown")
async def shutdown():
    mqtt_disconnect()
    await database.disconnect()

# # test routes
# @app.get("/", tags=["test"])
# def get_root():
#     return {"result": "Hello, World!"}
#
#
# @app.get("/items/{item_id}", tags=["test"])
# def get_item(item_id: int, q: str = None):
#     return {"id": item_id, "q": q}


app.include_router(crud_types_router, prefix=f'{api_prefix}{types_path}', tags=["Device types"])
app.include_router(crud_devices_router, prefix=f'{api_prefix}{devices_path}', tags=["Devices"])
app.include_router(crud_journal, prefix=f'{api_prefix}{journal_path}', tags=["Journal data"])
app.include_router(gate_mqtt, prefix=f'{api_prefix}{mqtt_path}', tags=["MQTT Gateway (FIXME!: Dev only)"])
