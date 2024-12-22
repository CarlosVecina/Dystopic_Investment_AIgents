import os

from sqlalchemy import create_engine

from dystopic_investment_aigents.data_ingestion.db.postgres_db import PostgresConfig

db_uri = PostgresConfig(
    host=os.environ["SB_DDBB_HOST"],
    port=os.environ["SB_DDBB_PORT"],
    database=os.environ["SB_DDBB_DATABASE"],
    user=os.environ["SB_DDBB_USER"],
    password=os.environ["SB_DDBB_PWD"],
).get_connection_string()

supabase_engine = create_engine(db_uri)
