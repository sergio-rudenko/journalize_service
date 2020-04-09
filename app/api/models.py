from typing import List
from pydantic import BaseModel, constr
from datetime import datetime

class DeviceType(BaseModel):
    title: constr(strip_whitespace=True, max_length=32)
    description: constr(strip_whitespace=True, max_length=254)


class DeviceTypeOut(DeviceType):
    id: int


class Device(BaseModel):
    type: int
    title: constr(strip_whitespace=True, max_length=64)
    description: constr(strip_whitespace=True, max_length=254)


class DeviceOut(Device):
    id: int


class JournalRecord(BaseModel):
    key: constr(strip_whitespace=True, min_length=1)
    value: constr(strip_whitespace=True, min_length=1)


class JournalIn(JournalRecord):
    device_id: int


class JournalOut(JournalIn):
    id: int
    dt: datetime


class DeviceJournalRecord(JournalRecord):
    type: constr(strip_whitespace=True, max_length=32)
    uuid: constr(strip_whitespace=True, max_length=64)