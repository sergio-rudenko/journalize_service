from typing import List
from fastapi import APIRouter, HTTPException

from app.api.models import Device, DeviceOut
from app.db import database, devices_table as table

router = APIRouter()


@router.post('/', status_code=201)
async def add_device(payload: Device):
    query = (table.insert().values(**payload.dict()))
    last_id = await database.execute(query=query)
    return {
        **payload.dict(),
        'id': last_id
    }


@router.get('/', response_model=List[DeviceOut])
async def get_device_list():
    query = table.select()
    device_list = await database.fetch_all(query=query)
    return device_list


@router.get('/{type_id}', response_model=List[DeviceOut])
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


@router.put('/{type_id}/{device_id}')
async def update_device_type_record(type_id: int, device_id: int, payload: Device):
    record = await get_device_record(type_id, device_id)
    if not record:
        raise HTTPException(status_code=404, detail="device not found")
    query = (
        table
        .update()
        .where(table.columns.type == type_id)
        .where(table.columns.id == device_id)
        .values(**payload.dict())
    )
    return await database.execute(query=query)


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

