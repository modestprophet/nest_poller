import os
import hvac
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# for vault authentication
VAULT_ADDR = os.environ.get("VAULT_ADDR")
VAULT_ROLE_ID = os.environ.get("VAULT_ETL_ROLE_ID")
VAULT_SECRET_ID = os.environ.get("VAULT_ETL_SECRET_ID")

# setup vault client
# TODO:  Handle the ConnectionError thrown when vault service isn't running on the server
multipass = hvac.Client(url=VAULT_ADDR)
multipass.auth.approle.login(VAULT_ROLE_ID, VAULT_SECRET_ID)

# app db
DB_URL = {'drivername': 'postgresql+psycopg2',
          'username': multipass.read('secret/etl/db/user')['data']['user'],
          'password': multipass.read('secret/etl/db/password')['data']['password'],
          'host': '10.0.20.18',
          'port': 5432,
          'database': 'plumbus'}

output_excel_path = r'C:\Users\Desktop\Desktop\blog\climate_data.xlsx'
output_path = r'C:\Users\Desktop\Desktop\blog\csv'

# each entry in this dict is 'excel_sheet_name: """SQL script"""
sql = {
    'raw_nest_thermostat_readings': '''
    select *,
        ((temperature * 9/5) + 32) as temperature_f,
        ((temperature * 9/5) + 32) as cool_temp_f,
        ((temperature * 9/5) + 32) as heat_temp_f
    from climate.raw_nest_thermostat_readings where time_created >= '2022-06-01';
    ''',
    'raw_printer_readings': '''
    select *,
       sensor_timestamp at time zone 'utc' at time zone 'cst' as sensor_timestamp_cst,
       ((temperature * 9/5) + 32) as temperature_f
    from climate.raw_printer_readings;
    ''',
    'outdoor_hourly_iaq': '''
    select moh.*,
       (select avg(moh2.pm25_env_avg)
        from climate.mqt_outdoor_hourly moh2
        where moh2.sensor_timestamp_hour >= moh.sensor_timestamp_hour - interval '12 hour' and
              moh2.sensor_timestamp_hour <= moh.sensor_timestamp_hour + interval '11 hour'
       ) as midpoint_pm25_env_avg,
       (select count(*)
        from climate.mqt_outdoor_hourly moh2
        where moh2.sensor_timestamp_hour >= moh.sensor_timestamp_hour - interval '12 hour' and
              moh2.sensor_timestamp_hour <= moh.sensor_timestamp_hour + interval '11 hour'
       ) as hour_count,
       sensor_timestamp_hour at time zone 'utc' at time zone 'cst' as sensor_timestamp_hour_cst
    from climate.mqt_outdoor_hourly moh;   
    ''',
    'printer_hourly_iaq': '''
    select moh.*,
       (select avg(moh2.pm25_env_avg)
        from climate.mqt_printer_hourly moh2
        where moh2.sensor_timestamp_hour >= moh.sensor_timestamp_hour - interval '12 hour' and
                moh2.sensor_timestamp_hour <= moh.sensor_timestamp_hour + interval '11 hour'
       ) as midpoint_pm25_env_avg,
       (select count(*)
        from climate.mqt_printer_hourly moh2
        where moh2.sensor_timestamp_hour >= moh.sensor_timestamp_hour - interval '12 hour' and
                moh2.sensor_timestamp_hour <= moh.sensor_timestamp_hour + interval '11 hour'
       ) as hour_count,
       sensor_timestamp_hour at time zone 'utc' at time zone 'cst' as sensor_timestamp_hour_cst
    from climate.mqt_printer_hourly moh;
    ''',
    'raw_outdoor_readings': '''
    select *,
       sensor_timestamp at time zone 'utc' at time zone 'cst' as sensor_timestamp_cst,
       ((temperature * 9/5) + 32) as temperature_f
    from climate.raw_outdoor_readings;
    ''',
    'raw_printer_status': '''
    select *,
       timestamp at time zone 'utc' at time zone 'cst' as timestamp_cst
    from printer.raw_printer_status;
    '''
}
