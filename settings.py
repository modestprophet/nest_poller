import os
import hvac
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# for vault authentication
VAULT_ADDR = os.environ.get("VAULT_ADDR")
VAULT_ROLE_ID = os.environ.get("VAULT_ROLE_ID")
VAULT_SECRET_ID = os.environ.get("VAULT_SECRET_ID")

# setup vault client
class VaultAuthenticator:
    def __init__(self, vault_addr, vault_role_id, vault_secret_id):
        self.vault_role_id = vault_role_id
        self.vault_secret_id = vault_secret_id
        self.vault = hvac.Client(url=vault_addr)

    def login(self):
        self.vault.auth.approle.login(self.vault_role_id, self.vault_secret_id)


multipass = VaultAuthenticator(VAULT_ADDR, VAULT_ROLE_ID, VAULT_SECRET_ID)
multipass.login()

# app db
DB_URL = {'drivername': 'postgresql+psycopg2',
          'username': multipass.vault.read('secret/nest/db/user')['data']['user'],
          'password': multipass.vault.read('secret/nest/db/password')['data']['password'],
          'host': '10.0.20.18',
          'port': 5432,
          'database': 'plumbus'}

# google oauth & api
TOKEN = multipass.vault.read('secret/nest/oauth/token')['data']['token']
SCOPES = ['https://www.googleapis.com/auth/sdm.service']
API_SERVICE_NAME = 'smartdevicemanagement'
API_VERSION = 'v1'
ENTERPRISE_PARENT = os.environ.get('ENTERPRISE_PARENT')
