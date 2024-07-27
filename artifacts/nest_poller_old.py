import sys
import settings
import google.oauth2.credentials
import google.auth.transport.requests
import googleapiclient.discovery

from models import NestReading
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker

import time
starttime = time.time()
while True:
    try:
        # print("Polling")
        # poll google api
        settings.TOKEN = settings.multipass.read('secret/nest/oauth/token')['data']['token']
        credentials = google.oauth2.credentials.Credentials(token=settings.TOKEN)

        sdm = googleapiclient.discovery.build(
            settings.API_SERVICE_NAME, settings.API_VERSION, credentials=credentials)

        devices = sdm.enterprises().devices().list(parent=settings.ENTERPRISE_PARENT).execute()
        traits = devices['devices'][0]['traits']
        sdm.close()


        # prepare output dict
        thermostat_reading = {}
        thermostat_reading['status'] = traits['sdm.devices.traits.Connectivity']['status']
        thermostat_reading['humidity'] = traits["sdm.devices.traits.Humidity"]["ambientHumidityPercent"]
        thermostat_reading['temperature'] = traits["sdm.devices.traits.Temperature"]["ambientTemperatureCelsius"]
        thermostat_reading['hvac_mode'] = traits["sdm.devices.traits.ThermostatHvac"]['status']

        # Heating/cooling target temp may not be present depending on if the thermostat is set to heat, cool, or both
        if "heatCelsius" in traits["sdm.devices.traits.ThermostatTemperatureSetpoint"]:
            thermostat_reading['heat_temp'] = traits["sdm.devices.traits.ThermostatTemperatureSetpoint"]["heatCelsius"]
        else:
            thermostat_reading['heat_temp'] = None

        if "coolCelsius" in traits["sdm.devices.traits.ThermostatTemperatureSetpoint"]:
            thermostat_reading['cool_temp'] = traits["sdm.devices.traits.ThermostatTemperatureSetpoint"]["coolCelsius"]
        else:
            thermostat_reading['cool_temp'] = None

        if "timerTimeout" in traits["sdm.devices.traits.Fan"]:
            thermostat_reading['fan_timeout'] = traits["sdm.devices.traits.Fan"]["timerTimeout"]


        # write data to db
        engine = create_engine(URL.create(**settings.DB_URL))
        Session = sessionmaker(engine)
        session = Session()

        NestReading.__table__.create(bind=engine, checkfirst=True)
        row_out = NestReading(**thermostat_reading)
        session.add(row_out)
        session.commit()
        print("Committed row")
        sys.stdout.flush()  # convince ubuntu to write stdout print statements to the journal
        # to see systemd unit log:  sudo journalctl -r -u nest-poller

    #####################################################################################################
        time.sleep(60.0 - ((time.time() - starttime) % 60.0))
    except Exception as err:
        print(f"Pull failed with exception: {err}")
        # TODO:  Implement a better fix for handling Vault permission denied errors.  for now just re-auth
        settings.multipass.auth.approle.login(settings.VAULT_ROLE_ID, settings.VAULT_SECRET_ID)
        time.sleep(60.0 - ((time.time() - starttime) % 60.0))

