from typing import List
from fastapi import APIRouter, HTTPException

from app.api.models import DeviceType, DeviceTypeOut
from app.db import database, types_table as table

router = APIRouter()


@router.post('/', status_code=201)
async def add_device_type_record(payload: DeviceType):
    query = table.insert().values(**payload.dict())
    last_id = await database.execute(query=query)
    return {
        **payload.dict(),
        'id': last_id
    }


@router.get('/', response_model=List[DeviceTypeOut])
async def get_device_type_list():
    query = table.select()
    list = await database.fetch_all(query=query)
    return list


@router.get('/{type_id}', response_model=DeviceType)
async def get_device_type_record(type_id: int):
    query = table.select(table.columns.id == type_id)
    record = await database.fetch_one(query=query)
    if not record:
        raise HTTPException(status_code=404, detail="given id not found")
    return record


@router.put('/{type_id}')
async def update_device_type_record(type_id: int, payload: DeviceType):
    record = await get_device_type_record(type_id)
    if not record:
        raise HTTPException(status_code=404, detail="given id not found")
    query = (
        table
        .update()
        .where(table.columns.id == type_id)
        .values(**payload.dict())
    )
    return await database.execute(query=query)


@router.delete('/{type_id}', status_code=403, response_description='delete not supported')
async def delete_device_type_record(type_id: int):
    raise HTTPException(status_code=403, detail="delete not supported")
