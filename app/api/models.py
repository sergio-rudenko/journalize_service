from typing import List
from pydantic import BaseModel, constr


class DeviceType(BaseModel):
    title: constr(strip_whitespace=True, max_length=4)
    description: constr(strip_whitespace=True, max_length=254)


class DeviceTypeOut(DeviceType):
    id: int


class Device(BaseModel):
    type: int
    title: constr(strip_whitespace=True, max_length=64)
    description: constr(strip_whitespace=True, max_length=254)


class DeviceOut(Device):
    id: int


class Journal(BaseModel):
    device_id: int
    key: constr(strip_whitespace=True, min_length=1)
    value: constr(strip_whitespace=True, min_length=1)


class JournalOut(Journal):
    id: int

