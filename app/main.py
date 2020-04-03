from fastapi import FastAPI

from app.api.crud_device_types import router as crud_types_router
from app.api.crud_devices import router as crud_devices_router
from app.api.crud_journal import router as crud_journal

from app.db import metadata, database, engine

from app.mqtt import mqtt_connect, mqtt_disconnect

metadata.create_all(engine)

api_version = '/v1'
api_prefix = '/api' + api_version

app = FastAPI(
    version="0.0.1",
    title="Journalize",
    description="Service to store data from MQTT device topic to Postgres database",
    redoc_url=api_prefix + '/redoc',
    docs_url=api_prefix + '/docs'
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


app.include_router(crud_types_router, prefix=api_prefix + '/types', tags=["Device types"])
app.include_router(crud_devices_router, prefix=api_prefix + '/devices', tags=["Devices"])
app.include_router(crud_journal, prefix=api_prefix + '/journal', tags=["Journal data"])
