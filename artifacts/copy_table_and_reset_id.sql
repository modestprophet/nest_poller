INSERT INTO climate.raw_nest_thermostat_readings
SELECT * from nest.thermostat;

-- Login to psql and run the following

-- What is the result?
SELECT MAX(id) FROM climate.raw_nest_thermostat_readings;

-- Then run...
-- This should be higher than the last result.
SELECT nextval('climate.raw_nest_thermostat_id_seq');

-- If it's not higher... run this set the sequence last to your highest id. 
-- (wise to run a quick pg_dump first...)

BEGIN;
-- protect against concurrent inserts while you update the counter
LOCK TABLE climate.raw_nest_thermostat_readings IN EXCLUSIVE MODE;
-- Update the sequence
SELECT setval('climate.raw_nest_thermostat_id_seq', COALESCE((SELECT MAX(id)+1 FROM climate.raw_nest_thermostat_readings), 1), false);
COMMIT;