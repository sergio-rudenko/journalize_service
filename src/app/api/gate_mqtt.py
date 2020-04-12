from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, constr

from app.mqtt import mqtt_publish

router = APIRouter()


class MqttMessage(BaseModel):
    topic: constr(strip_whitespace=True, min_length=1)
    data: constr(strip_whitespace=True, min_length=1)


@router.post('/', status_code=201)
async def add_device(payload: MqttMessage):
    mqtt_publish(payload.topic, payload.data)
    return None
