from typing import List
from fastapi import APIRouter, HTTPException

from app.api.models import DeviceType, DeviceTypeOut
from app.db import database, types_table as table

router = APIRouter()


# database functions ---------------------------------------------------------
async def fetch_device_type_record_by_title(title: str):
    query = table.select(table.columns.title == title)
    record = await database.fetch_one(query=query)
    if record:
        return record
    return None


# CRUD -----------------------------------------------------------------------
@router.post('/', status_code=201, response_model=int)
async def add_device_type_record(payload: DeviceType):
    record = await  fetch_device_type_record_by_title(payload.title)
    if record:
        raise HTTPException(status_code=409, detail="already exists")
    query = table.insert().values(**payload.dict())
    last_id = await database.execute(query=query)
    return last_id


@router.get('/', response_model=int)
async def get_device_type_id(q: str = None):
    if not q:
        raise HTTPException(status_code=400, detail="parameter required")
    record = await fetch_device_type_record_by_title(q)
    if not record:
        raise HTTPException(status_code=404, detail="given type not found")
    return int(record['id'])


@router.get('/all/', response_model=List[DeviceTypeOut])
async def get_device_type_list():
    query = table.select()
    return await database.fetch_all(query=query)


@router.get('/{type_id}', response_model=DeviceType)
async def get_device_type_record(type_id: int):
    query = table.select(table.columns.id == type_id)
    record = await database.fetch_one(query=query)
    if not record:
        raise HTTPException(status_code=404, detail="given id not found")
    return record


# @router.put('/{type_id}')
# async def update_device_type_record(type_id: int, payload: DeviceType):
#     record = await get_device_type_record(type_id)
#     if not record:
#         raise HTTPException(status_code=404, detail="given id not found")
#     query = (
#         table
#         .update()
#         .where(table.columns.id == type_id)
#         .values(**payload.dict())
#     )
#     return await database.execute(query=query)


@router.delete('/{type_id}', status_code=403, response_description='delete not supported')
async def delete_device_type_record(type_id: int):
    raise HTTPException(status_code=403, detail="delete not supported")
