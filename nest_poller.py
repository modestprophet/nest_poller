import settings
import google.oauth2.credentials
import google.auth.transport.requests
import googleapiclient.discovery
from models import NestReading
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NestAPI:
    def __init__(self, credentials, vault_authenticator):
        self.credentials = credentials
        self.vault_authenticator = vault_authenticator
        self.sdm =  self._create_sdm()

    def _create_sdm(self):
        return googleapiclient.discovery.build(
            settings.API_SERVICE_NAME, settings.API_VERSION, credentials=self.credentials, cache_discovery=False)

    def _refresh_sdm(self):
        self.sdm.close()
        self.sdm = self._create_sdm()

    def refresh_token(self):
        new_token = self.vault_authenticator.vault.read('secret/nest/oauth/token')['data']['token']
        self.credentials.token = new_token
        self._refresh_sdm()
        logger.info("Refreshed token and recreated SDM object")
    
    def get_devices(self):
        return self.sdm.enterprises().devices().list(parent=settings.ENTERPRISE_PARENT).execute()

    def close(self):
        self.sdm.close()


class NestDataReader:
    def __init__(self, nest_api):
        self.nest_api = nest_api

    def read_data(self):
        devices = self.nest_api.get_devices()
        traits = devices['devices'][0]['traits']
        data = {
            'status': traits['sdm.devices.traits.Connectivity']['status'],
            'humidity': traits["sdm.devices.traits.Humidity"]["ambientHumidityPercent"],
            'temperature': traits["sdm.devices.traits.Temperature"]["ambientTemperatureCelsius"],
            'hvac_mode': traits["sdm.devices.traits.ThermostatHvac"]['status'],
            'heat_temp': traits["sdm.devices.traits.ThermostatTemperatureSetpoint"].get("heatCelsius"),
            'cool_temp': traits["sdm.devices.traits.ThermostatTemperatureSetpoint"].get("coolCelsius"),
            'fan_timeout': traits["sdm.devices.traits.Fan"].get("timerTimeout")
        }
        return data


class NestDataWriter:
    def __init__(self, db_url):
        self.engine = create_engine(URL.create(**db_url))
        self.Session = sessionmaker(self.engine)

    def write_data(self, data):
        session = self.Session()
        NestReading.__table__.create(bind=self.engine, checkfirst=True)
        row_out = NestReading(**data)
        session.add(row_out)
        session.commit()
        logger.info("Committed row")


class NestPoller:
    def __init__(self, nest_api, data_reader, data_writer):
        self.nest_api = nest_api
        self.data_reader = data_reader
        self.data_writer = data_writer

    def poll(self):
        try:
            data = self.data_reader.read_data()
            self.data_writer.write_data(data)
        except google.auth.exceptions.RefreshError as err:
            logger.info(f"Token likely needs to be refreshed: {err}")
            self.nest_api.refresh_token()
        except Exception as err:
            logger.error(f"Pull failed with exception: {err}")

#####
def main():
    credentials = google.oauth2.credentials.Credentials(token=settings.TOKEN)
    nest_api = NestAPI(credentials, settings.multipass)
    data_reader = NestDataReader(nest_api)
    data_writer = NestDataWriter(settings.DB_URL)
    poller = NestPoller(nest_api, data_reader, data_writer)

    while True:
        poller.poll()
        time.sleep(60.0)


if __name__ == "__main__":
    main()
