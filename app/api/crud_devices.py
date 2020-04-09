from typing import List
from fastapi import APIRouter, HTTPException

from app.api.models import Device, DeviceOut
from app.db import database, devices_table as table

router = APIRouter()


# database functions ---------------------------------------------------------
async def fetch_device_record_by_title(type_id: int, title: str):
    query = (
        table
        .select()
        .where(table.columns.type == type_id)
        .where(table.columns.title == title)
    )
    record = await database.fetch_one(query=query)
    if record:
        return record
    return None


# CRUD -----------------------------------------------------------------------
@router.post('/', status_code=201, response_model=int)
async def add_device_record(payload: Device):
    record = await fetch_device_record_by_title(payload.type, payload.title)
    if record:
        raise HTTPException(status_code=409, detail="already exists")
    query = table.insert().values(**payload.dict())
    last_id = await database.execute(query=query)
    return last_id


@router.get('/{type_id}/', response_model=int)
async def get_device_id(type_id: int, q: str = None):
    if not q:
        raise HTTPException(status_code=400, detail="parameter required")
    record = await fetch_device_record_by_title(type_id, q)
    if not record:
        raise HTTPException(status_code=404, detail="device not found")
    return int(record['id'])


# @router.get('/', response_model=List[DeviceOut])
# async def get_device_list():
#     return await fetch_all_records(table)


@router.get('/{type_id}/all/', response_model=List[DeviceOut])
async def get_device_list_by_type(type_id: int):
    query = table.select(table.columns.type == type_id)
    device_list = await database.fetch_all(query=query)
    return device_list


@router.get('/{type_id}/{device_id}', response_model=DeviceOut)
async def get_device_record(type_id: int, device_id: int):
    query = (
        table
        .select()
        .where(table.columns.type == type_id)
        .where(table.columns.id == device_id)
    )
    record = await database.fetch_one(query=query)
    if not record:
        raise HTTPException(status_code=404, detail="device not found")
    return record


# @router.put('/{type_id}/{device_id}')
# async def update_device_type_record(type_id: int, device_id: int, payload: Device):
#     record = await get_device_record(type_id, device_id)
#     if not record:
#         raise HTTPException(status_code=404, detail="device not found")
#     query = (
#         table
#         .update()
#         .where(table.columns.type == type_id)
#         .where(table.columns.id == device_id)
#         .values(**payload.dict())
#     )
#     return await database.execute(query=query)


@router.delete('/{type_id}/{device_id}', status_code=403, response_description='delete not supported')
async def delete_device_type_record(type_id: int, device_id: int):
    raise HTTPException(status_code=403, detail="delete not supported")


# @router.delete('/{type_id}/{device_id}')
# async def delete_device_type_record(type_id: int, device_id: int):
#     record = await get_device_record(type_id, device_id)
#     if not record:
#         raise HTTPException(status_code=404, detail="device not found")
#     query = (
#         table
#         .delete()
#         .where(table.columns.type == type_id)
#         .where(table.columns.id == device_id)
#     )
#     # TODO: recursively delete journal records
#     return await database.execute(query=query)

