from typing import List
from datetime import datetime
from pydantic import BaseModel, constr


# base -----------------------------------------------------------------------
class JournalBase(BaseModel):
    key: constr(strip_whitespace=True)
    value: constr(strip_whitespace=True)

    class Config:
        orm_mode = True


class DeviceTypeBase(BaseModel):
    title: constr(strip_whitespace=True, max_length=32)
    description: constr(strip_whitespace=True, max_length=254)

    class Config:
        orm_mode = True


class DeviceBase(BaseModel):
    title: constr(strip_whitespace=True, max_length=64)
    description: constr(strip_whitespace=True, max_length=254)

    class Config:
        orm_mode = True


# journal --------------------------------------------------------------------
class JournalCreate(JournalBase):
    pass


class JournalRecord(JournalBase):
    dt: datetime


class Journal(JournalRecord):
    id: int
    device_id: int

    device: DeviceBase

    class Config:
        orm_mode = True


# devise types ---------------------------------------------------------------
class DeviceTypeCreate(DeviceTypeBase):
    pass


class DeviceType(DeviceTypeBase):
    id: int

    devices: List[DeviceBase] = []

    class Config:
        orm_mode = True


# devices --------------------------------------------------------------------
class DeviceCreate(DeviceBase):
    pass


class Device(DeviceBase):
    id: int
    type_id: int

    type: DeviceTypeBase
    records: List[JournalRecord] = []

    class Config:
        orm_mode = True

