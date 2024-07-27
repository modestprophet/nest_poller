from sqlalchemy import Column, Integer, Text, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class NestReading(Base):
    __tablename__ = 'raw_nest_thermostat_readings'
    __table_args__ = {'schema': 'climate'}
    id = Column(Integer, primary_key=True)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(Text, nullable=True)  # "sdm.devices.traits.Connectivity": {"status": "ONLINE"}
    fan_timeout = Column(DateTime, nullable=True)  # "sdm.devices.traits.Fan": {"timerMode": "ON", "timerTimeout": "2021-03-22T14:21:19Z"},
    humidity = Column(Integer, nullable=False)  # "sdm.devices.traits.Humidity": {"ambientHumidityPercent": 37},
    temperature = Column(Float, nullable=False)  # "sdm.devices.traits.Temperature": {"ambientTemperatureCelsius": 21.37999},
    hvac_mode = Column(Text, nullable=False)  # "sdm.devices.traits.ThermostatHvac": {"status": "HEATING"},
    heat_temp = Column(Float, nullable=True)  # "sdm.devices.traits.ThermostatTemperatureSetpoint": {"coolCelsius": 26.45842, "heatCelsius": 22.027618}
    cool_temp = Column(Float, nullable=True)

