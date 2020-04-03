from typing import List
from fastapi import APIRouter, HTTPException

from app.api.models import Journal, JournalOut
from app.db import database, journal_table as table

router = APIRouter()


@router.get('/{device_id}', response_model=List[JournalOut])
async def get_journal_record_list_by_device(device_id: int):
    query = table.select(table.columns.device_id == device_id)
    record_list = await database.fetch_all(query=query)
    return record_list


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
