from typing import List
from datetime import datetime
from fastapi import Depends, APIRouter, Header, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app import config, models, schemas

from app.api.crud_devices import obtain_device_type_id, get_device_type, obtain_device_id, get_device

router = APIRouter()


# Authorization functions ----------------------------------------------------
def check_authorised(token: str, admin_access_required: bool = False):
    if not admin_access_required:
        is_valid_token = False
        if token != config.ADMIN_TOKEN:
            for record in config.USER_TOKENS:
                if record["token"] == token:
                    print(f'Token "{record["token"]}" updated')
                    record["dt"] = datetime.now();  # update exp
                    is_valid_token = True;
        return token == config.ADMIN_TOKEN or is_valid_token
    else:
        return token == config.ADMIN_TOKEN


# Journal functions ----------------------------------------------------------
def add_journal_record(db: Session, record: schemas.JournalCreate, type_title: str, device_title: str):
    # print("add_journal_record:", record, db)
    type_id = obtain_device_type_id(db, type_title=type_title)
    # print("type_id:", type_id)
    device_id = obtain_device_id(db, type_id=type_id, device_title=device_title)
    # print("device_id:", device_id)
    db_record = models.Journal(**record.dict(), device_id=device_id)
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


def get_journal_records_list(db: Session, device_id: int,
                             dt_from: datetime, dt_to: datetime,
                             offset: int = 0, limit: int = 100):
    return db.query(models.Journal).filter(
        models.Journal.device_id == device_id,
        models.Journal.dt >= dt_from,
        models.Journal.dt < dt_to
    ).offset(offset).limit(limit).all()


def get_journal_record_keys_list(db: Session, device_id: int,
                                 offset: int = 0, limit: int = 100):
    result = db.query(models.Journal.key).filter(
        models.Journal.device_id == device_id
    ).distinct().offset(offset).limit(limit).all()

    # some hack, cause List of Lists returns
    keys: List[str] = []
    for row in result:
        keys.append(row[0])

    return keys


def get_journal_records_list_by_key(db: Session, device_id: int, key: str,
                                    dt_from: datetime, dt_to: datetime,
                                    offset: int = 0, limit: int = 100):
    return db.query(models.Journal).filter(
        models.Journal.device_id == device_id,
        models.Journal.key == key,
        models.Journal.dt >= dt_from,
        models.Journal.dt < dt_to
    ).offset(offset).limit(limit).all()


# CRUD -----------------------------------------------------------------------
@router.post('/{type_title}/{device_title}/records/', status_code=201, response_model=int)
def create_journal_record(type_title: str, device_title: str, payload: schemas.JournalCreate,
                          x_token: str = Header(...), db: Session = Depends(get_db)):
    if not check_authorised(token=x_token, admin_access_required=False):
        raise HTTPException(status_code=401, detail="Not Authorised")

    new_record = add_journal_record(db, payload, type_title=type_title, device_title=device_title)
    return new_record.id


@router.get('/{type_title}/{device_title}/records/', response_model=List[schemas.JournalRecord])
def read_journal_records_list(type_title: str, device_title: str,
                              dt_from: datetime = datetime.fromtimestamp(0),
                              dt_to: datetime = datetime.now(),
                              offset: int = 0, limit: int = 100,
                              x_token: str = Header(...),
                              db: Session = Depends(get_db)):
    if not check_authorised(token=x_token, admin_access_required=False):
        raise HTTPException(status_code=401, detail="Not Authorised")

    type_record = get_device_type(db, type_title=type_title)

    if not type_record:
        raise HTTPException(status_code=404, detail="type not found")

    device_record = get_device(db, type_id=type_record.id, device_title=device_title)

    if not device_record:
        raise HTTPException(status_code=404, detail="device not found")

    return get_journal_records_list(db, device_id=device_record.id,
                                    dt_from=dt_from, dt_to=dt_to,
                                    offset=offset, limit=limit)


@router.get('/{type_title}/{device_title}/keys/', response_model=List[str])
def read_journal_record_keys_list(type_title: str, device_title: str,
                                  offset: int = 0, limit: int = 100,
                                  x_token: str = Header(...),
                                  db: Session = Depends(get_db)):
    if not check_authorised(token=x_token, admin_access_required=False):
        raise HTTPException(status_code=401, detail="Not Authorised")

    type_record = get_device_type(db, type_title=type_title)

    if not type_record:
        raise HTTPException(status_code=404, detail="type not found")

    device_record = get_device(db, type_id=type_record.id, device_title=device_title)

    if not device_record:
        raise HTTPException(status_code=404, detail="device not found")

    return get_journal_record_keys_list(db, device_id=device_record.id,
                                        offset=offset, limit=limit)


@router.get('/{type_title}/{device_title}/keys/{key}', response_model=List[schemas.JournalRecord])
def read_journal_records_list_by_key(type_title: str, device_title: str, key: str,
                                     dt_from: datetime = datetime.fromtimestamp(0),
                                     dt_to: datetime = datetime.now(),
                                     offset: int = 0, limit: int = 100,
                                     x_token: str = Header(...),
                                     db: Session = Depends(get_db)):
    if not check_authorised(token=x_token, admin_access_required=False):
        raise HTTPException(status_code=401, detail="Not Authorised")

    type_record = get_device_type(db, type_title=type_title)

    if not type_record:
        raise HTTPException(status_code=404, detail="type not found")

    device_record = get_device(db, type_id=type_record.id, device_title=device_title)

    if not device_record:
        raise HTTPException(status_code=404, detail="device not found")

    return get_journal_records_list_by_key(db, device_id=device_record.id, key=key,
                                           dt_from=dt_from, dt_to=dt_to,
                                           offset=offset, limit=limit)
