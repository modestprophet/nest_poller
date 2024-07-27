/*
sudo -I -u dbadmin
psql -d plumbus
*/

CREATE ROLE nestpoller WITH LOGIN;
ALTER ROLE nestpoller WITH PASSWORD 'some_password';
GRANT USAGE ON SCHEMA public TO nestpoller;

CREATE SCHEMA climate;

GRANT USAGE ON SCHEMA climate TO nestpoller;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA climate TO nestpoller;
GRANT ALL ON ALL SEQUENCES IN schema climate TO nestpoller;

\q


/*
 this is what I used to change some columns to nullable after initially setting to not nullable
 ALTER TABLE climate.raw_nest_thermostat_readings ALTER COLUMN heat_temp DROP NOT NULL;
ALTER TABLE climate.raw_nest_thermostat_readings ALTER COLUMN cool_temp DROP NOT NULL;
 */