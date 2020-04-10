from typing import List
from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app import models, schemas

router = APIRouter()


# Device Type functions ------------------------------------------------------
def add_device_type(db: Session, device_type: schemas.DeviceTypeCreate):
    db_device_type = models.DeviceType(**device_type.dict())
    db.add(db_device_type)
    db.commit()
    db.refresh(db_device_type)
    return db_device_type


def obtain_device_type_id(db: Session, type_title: str):
    type_record = get_device_type(db, type_title=type_title)

    if not type_record:
        type_record = add_device_type(db, schemas.DeviceTypeCreate(
            title=type_title, description='created by api'))

    return type_record.id


# def get_device_type_by_id(db: Session, type_id: int):
#     return db.query(models.DeviceType).filter(models.DeviceType.id == type_id).first()


def get_device_type(db: Session, type_title: str):
    return db.query(models.DeviceType).filter(models.DeviceType.title == type_title).first()


def get_device_types_list(db: Session, offset: int = 0, limit: int = 100):
    return db.query(models.DeviceType).offset(offset).limit(limit).all()


# Device functions -----------------------------------------------------------
def add_device(db: Session, device: schemas.DeviceCreate, type_id: int):
    db_device = models.Device(**device.dict(), type_id=type_id)
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device


def obtain_device_id(db: Session, type_id: int, device_title: str):
    device_record = get_device(db, type_id=type_id, device_title= device_title)

    if not device_record:
        device_record = add_device(db, schemas.DeviceCreate(
            title=device_title, description='created by api'), type_id=type_id)

    return device_record.id


# def get_device_by_id(db: Session, device_id: int):
#     return db.query(models.Device).filter(models.Device.id == device_id).first()


def get_device(db: Session, type_id: int, device_title: str):
    return db.query(models.Device).filter(
        models.Device.type_id == type_id,
        models.Device.title == device_title
    ).first()


def get_devices_list(db: Session, type_id: int, offset: int = 0, limit: int = 100):
    return db.query(models.Device).filter(
        models.Device.type_id == type_id
    ).offset(offset).limit(limit).all()

# TODO: Update and Delete


# CRUD Types -----------------------------------------------------------------
@router.post('/types/', status_code=201, response_model=int)
def create_device_type(payload: schemas.DeviceTypeCreate, db: Session = Depends(get_db)):
    if get_device_type(db, type_title=payload.title):
        raise HTTPException(status_code=400, detail="type already exists")

    new_record = add_device_type(db, payload)
    return new_record.id


@router.get('/types', response_model=List[schemas.DeviceType])
def read_device_types_list(offset: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_device_types_list(db, offset, limit)


@router.get('/{type_title}', response_model=schemas.DeviceType)
def read_device_type(type_title: str = None, db: Session = Depends(get_db)):
    type_record = get_device_type(db, type_title=type_title)

    if not type_record:
        raise HTTPException(status_code=404, detail="type not found")

    return type_record


# CRUD Devices ---------------------------------------------------------------
@router.post('/{type_title}/devices/', status_code=201, response_model=int)
def create_device(type_title: str, payload: schemas.DeviceCreate, db: Session = Depends(get_db)):
    type_record = obtain_device_type_id(db, type_title=type_title)
    if get_device(db, type_id=type_record.id, device_title=payload.title):
        raise HTTPException(status_code=400, detail="device already exists")

    new_record = add_device(db, payload, type_id=type_record.id)
    return new_record.id


@router.get('/{type_title}/devices', response_model=List[schemas.Device])
def read_devices_list(type_title: str, offset: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    type_record = get_device_type(db, type_title)

    if not type_record:
        raise HTTPException(status_code=404, detail="type not found")

    return get_devices_list(db, type_record.id, offset, limit)


@router.get('/{type_title}/{device_title}', response_model=schemas.Device)
def read_device(type_title: str, device_title: str, db: Session = Depends(get_db)):
    type_record = get_device_type(db, type_title=type_title)

    if not type_record:
        raise HTTPException(status_code=404, detail="type not found")

    device_record = get_device(db, type_id=type_record.id, device_title=device_title)

    if not device_record:
        raise HTTPException(status_code=404, detail="device not found")

    return device_record
