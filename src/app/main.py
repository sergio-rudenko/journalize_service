import os
import time

from fastapi import FastAPI, Request, Header, HTTPException
from uvicorn.main import Server

from app import models
from app.api.crud_devices import router as crud_devices_router
from app.api.crud_journal import router as crud_journal_router
from app.config import title, version, api_version, api_prefix
from app.db import engine
from app.mqtt import mqtt_connect, mqtt_disconnect

models.Base.metadata.create_all(bind=engine)


# [shutdown handle] ----------------------------------------------------------
original_handle_exit = Server.handle_exit


class ShutdownHandler:
    @staticmethod
    def handle_exit(*args, **kwargs):
        # print("Shutdown app..", args)
        mqtt_disconnect()
        original_handle_exit(*args, **kwargs)


Server.handle_exit = ShutdownHandler.handle_exit
# ----------------------------------------------------------------------------

app = FastAPI(
    version=version,
    title=title,
    description="Service to store data from MQTT device topic to Postgres database",
    redoc_url=f'{api_prefix}/redoc',
    docs_url=f'{api_prefix}/docs',
    openapi_prefix=os.getenv('SERVICE_PREFIX', '/journal')
)


@app.on_event("startup")
async def startup():
    print("on_event: startup")
    mqtt_connect()
    return None


@app.on_event("shutdown")
async def shutdown():
    print("on_event: shutdown")
    return None


# https://fastapi.tiangolo.com/tutorial/middleware/
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    # TODO: dirty check 'X-Token'
    # print("request:", request.headers)
    # if 'x-token' not in request.headers:
    #     response = Response(
    #         status_code=401,
    #         content='{"detail": "read the docs, provide token"}',
    #         media_type="application/json"
    #     )
    #     return response
    #
    # if request.headers['x-token'] != '11223344':
    #     response = Response(
    #         status_code=401,
    #         content='{"detail": "token is not valid"}',
    #         media_type="application/json"
    #     )
    #     return response

    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)

    if 'x-token' in request.headers:
        response.headers["X-Token-Received"] = request.headers['x-token']
    else:
        response.headers["X-Token-Received"] = "none"

    return response


# test routes
@app.get("/", tags=["root"])
def get_path():
    return {"path": f"{api_prefix}", "version": f"{api_version}"}


@app.get("/test", tags=["root"])
def get_test(x_token: str = Header(...)):
    if not x_token:
        raise HTTPException(status_code=401, detail="token required")
    return {"msg": "Hello World"}


# @app.get("/items/{item_id}", tags=["test"])
# def get_item(item_id: int, q: str = None):
#     return {"id": item_id, "q": q}

app.include_router(crud_devices_router, prefix=f'{api_prefix}', tags=["Devices"])
app.include_router(crud_journal_router, prefix=f'{api_prefix}', tags=["Journal"])
