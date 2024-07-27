import refresh_excel_settings as settings
import pandas as pd
import datetime

# from models import OutdoorClimateReading
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker

engine = create_engine(URL.create(**settings.DB_URL))
session_engine = sessionmaker(engine)
session = session_engine()
#OutdoorClimateReading.__table__.create(bind=engine, checkfirst=True)



def main():
    # with pd.ExcelWriter(settings.output_excel_path) as writer:
        for sheet, query in settings.sql.items():
            print(f'Processing {sheet}')
            df = pd.read_sql_query(query, engine)
            # date_columns = df.select_dtypes(include=['datetimetz', 'datetime64[ns]', 'datetime64[ns, UTC]']).columns
            # for date_column in date_columns:
            #     df[date_column] = df[date_column].apply(lambda a: datetime.datetime.strftime(a,"%Y-%m-%d %H:%M:%S")).where(df[date_column].notnull(), None)
            #     df[date_column] = pd.to_datetime(df[date_column])
            # if 'time_created' in df.columns:
            #     df['time_created'] = df['time_created'].apply(lambda a: datetime.datetime.strftime(a,"%Y-%m-%d %H:%M:%S"))
            #     df['time_created'] = pd.to_datetime(df['time_created'])
            # df.to_excel(writer,
            #             sheet_name=sheet)

            df.to_csv(fr'{settings.output_path}\{sheet}.tsv', sep='\t', encoding='utf-8', index=False)


    # query.close()

if __name__ == '__main__':
    main()
