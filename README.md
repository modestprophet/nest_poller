# Nest Poller
A simple polling service for the Nest Thermostat.  Polls your Nest thermostat once a minute and stores the results in a Postgres database.  Designed to run as a service on a server somewhere.  This implementation uses Hashicorp Vault for secrets management.  

### OAuth stuff
You'll need to do some work in the maze of google OAuth stuff to generate the necessary keys and auth stuff to poll the Nest API.
- google docs:  https://developers.google.com/nest/device-access/get-started
- helpful example blog:  https://geoffhudik.com/tech/2023/03/04/trying-google-nest-api-with-postman-and-python/

#### Note on google OAuth key rotation
The google OAuth token needed to poll the Nest API expires after 60 minutes and needs to be refreshed periodically.  This implementation assumes the latest token is available in Vault and assumes there is a separate service that rotates the OAuth token and stores it in Vault.  In theory this improves security by creating some separation between the application accessing the Nest API and the super secret client_secret and refresh tokens.  Probably total overkill for most home applications but I wanted to experiment with trying to do things the Right Way™


### Config notes
- Check settings.py for config stuff.  You'll need to modify the database connect info and Vault secrets paths.
- You'll need to create a .env to load some environment variables.  Check sample.env for the needed keys

#### Install as a service on some server

- copy files to deployment server (e.g., git pull)
- cd to directory
- create the venv:  ```python venv .venv```
- activate venv:  ```source .venv/bin/activate```
- install python reqs:  ```pip install -r requirements.txt```
- copy service file:  ```cp ~/nest-poller.service /etc/systemd/system/nest-poller.service```
- ```sudo systemctl daemon-reload```
- ```sudo systemctl start nest-poller.service```
- check it's running:  ```sudo systemctl status nest-poller.service```a

TODO: Move google enterprise parent ID from .env to Vault