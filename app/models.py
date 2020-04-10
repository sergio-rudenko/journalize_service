from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db import Base


class DeviceType(Base):
    __tablename__ = "types"

    id = Column(Integer, primary_key=True)
    title = Column(String(32), unique=True, nullable=False)
    description = Column(String(254))
    created = Column(DateTime, default=func.now(), nullable=False)
    updated = Column(DateTime, default=func.now(), nullable=False)

    devices = relationship("Device", order_by="Device.id", back_populates="type")


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True)
    type_id = Column(Integer, ForeignKey("types.id"))

    title = Column(String(64), unique=True, nullable=False)
    description = Column(String(254))
    created = Column(DateTime, default=func.now(), nullable=False)
    updated = Column(DateTime, default=func.now(), nullable=False)

    type = relationship("DeviceType", back_populates="devices")
    records = relationship("Journal", back_populates="device")


class Journal(Base):
    __tablename__ = "journal"

    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey("devices.id"))

    key = Column(String(), nullable=False)
    value = Column(String(), nullable=False)
    dt = Column(DateTime, default=func.now(), nullable=False)

    device = relationship("Device", back_populates="records")
