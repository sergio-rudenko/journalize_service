from typing import List
from datetime import datetime

from fastapi import APIRouter, HTTPException

from app.api.models import JournalIn, JournalOut
from app.db import database, journal_table as table

from app.api.crud_device_types import fetch_device_type_record_by_title
from app.api.crud_devices import fetch_device_record_by_title

router = APIRouter()


# FIXME! get journal records by type/uuid

@router.post('/', status_code=201, response_model=int)
async def add_journal_record(payload: JournalIn):
    if not payload.device_id:
        raise HTTPException(status_code=400, detail="device_id required")
    query = (
        table
        .insert()
        .values({
            'device_id': payload.device_id,
            'key': payload.key,
            'value': payload.value
        })
    )
    last_id = await database.execute(query=query)
    return last_id


@router.get('/', response_model=List[JournalOut])
async def get_journal_record_list_by_device(type: str = None, uuid: str = None):
    device_type_record = await fetch_device_type_record_by_title(type)
    if not device_type_record:
        raise HTTPException(status_code=404, detail="given type does not exists")
    device_record = await fetch_device_record_by_title(device_type_record['id'], uuid)
    if not device_record:
        raise HTTPException(status_code=404, detail="given uuid does not exists")
    query = (
        table
        .select()
        .where(table.columns.device_id == device_record['id'])
        # FIXME! time constraints
        .limit(100)
    )
    record_list = await database.fetch_all(query=query)
    return record_list


@router.get('/{device_type}/{device_title}', response_model=List[JournalOut])
async def get_journal_records(device_type: str, device_title: str,
                              dt_from: datetime = 0, dt_to: datetime = datetime.now()):
    print(f'from: {dt_from} to: {dt_to}')
    query = (

    )


@router.get('/{device_id}/{record_id}', response_model=JournalOut)
async def get_journal_record(device_id: int, record_id: int):
    query = (
        table
        .select()
        .where(table.columns.device_id == device_id)
        .where(table.columns.id == record_id)
    )
    record = await database.fetch_one(query=query)
    if not record:
        raise HTTPException(status_code=404, detail="record not found")
    return record
