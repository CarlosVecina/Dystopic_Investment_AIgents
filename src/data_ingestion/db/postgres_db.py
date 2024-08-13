import datetime
import pandas as pd
from sqlalchemy import MetaData, Table, create_engine, text


class PostgresConfig:
    def __init__(self, host, port, database, user, password):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password

    def get_connection_string(self):
        return f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


class PostgresDB:
    def __init__(self, config: PostgresConfig):
        self.config = config
        self.engine = create_engine(self.config.get_connection_string())
        self.connection = self.engine.connect()
        self.metadata = MetaData()
        # self.metadata.reflect(self.engine)

    def query(self, query_string):
        return self.connection.execute(query_string)

    def insert(self, table_name, data):
        table = Table(table_name, self.metadata, autoload_with=self.engine)
        self.connection.execute(table.insert(), data)


class FinancialDB(PostgresDB):
    def get_top_volume_tickers(self, top_n: int | None = 100) -> pd.DataFrame:
        limit = ""
        if top_n:
            limit = f"LIMIT {top_n}"

        return pd.read_sql(
            f"""
            SELECT *, Row_number()OVER() as top_n
            FROM (
                SELECT ticker, max(close * volume) as daily_volume FROM ticker_prices WHERE close is not null GROUP BY 1 ORDER BY daily_volume DESC {limit}
            ) a
            """,
            self.engine,
        )["ticker"].to_list()

    def get_available_tickers(
        self, date: datetime.datetime | None = None
    ) -> list[str] | None:
        if not date:
            date = pd.read_sql(
                text("SELECT max(created_at) FROM active_tickers"),
                self.engine,
            )["max"].to_list()[0]

        return pd.read_sql(
            text(
                "SELECT ticker FROM active_tickers WHERE created_at = :filter_date"
            ),
            self.engine,
            params={"filter_date": date},
        )["ticker"].to_list()
