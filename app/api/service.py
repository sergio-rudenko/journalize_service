# import  os
import httpx

from app.api.models import JournalRecord, JournalIn
from app.config import api_prefix, types_path, devices_path, journal_path

url = 'http://127.0.0.1:8000'
device_types_url = f'{url}{api_prefix}{types_path}'
devices_url = f'{url}{api_prefix}{devices_path}'
journal_url = f'{url}{api_prefix}{journal_path}'


def get_device_type_id(device_type_title: str, create_if_needed: bool = True) -> int:
    params = {
        'q': device_type_title
    }
    result = httpx.get(f'{device_types_url}/', params=params)
    if result.status_code == 200:
        return int(result.text)
    if result.status_code == 404 and create_if_needed:
        payload = {
            'title': device_type_title,
            'description': 'created from get_device_type_id'
        }
        post = httpx.post(f'{device_types_url}/', json=payload)
        if post.status_code == 201:
            return int(post.text)
    return 0


def get_device_id(type_id: int, device_title: str, create_if_needed: bool = True) -> int:
    params = {
        'q': device_title
    }
    result = httpx.get(f'{devices_url}/{type_id}/', params=params)
    if result.status_code == 200:
        return int(result.text)
    if result.status_code == 404 and create_if_needed:
        payload = {
            'type': type_id,
            'title': device_title,
            'description': 'created from get_device_id'
        }
        post = httpx.post(f'{devices_url}/', json=payload)
        if post.status_code == 201:
            return int(post.text)
    return 0


def add_device_journal_record(device_type: str, device_uuid: str, data: JournalRecord):
    print("add_device_journal_record:", data)
    type_id = get_device_type_id(device_type)
    if not type_id:
        print(f"ERROR! no type_id for '{device_type}'")
        return None
    device_id = get_device_id(type_id, device_uuid)
    if not type_id:
        print(f"ERROR! no device_id for '{device_uuid}'")
        return None

    print(f"{device_type}/{device_uuid} device_id:", device_id)
    result = httpx.post(f'{journal_url}/', json={"device_id": device_id, 'key': data.key, 'value': data.value})
    if result.status_code != 201:
        print(f'{device_type}/{device_uuid}, "{data.key}" -> "{data.value} ERROR:', result.text)
    else:
        print('saved:', data)
