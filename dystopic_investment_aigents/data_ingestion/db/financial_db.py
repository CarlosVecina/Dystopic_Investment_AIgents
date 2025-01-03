import datetime

import pandas as pd
from sqlalchemy import text

from dystopic_investment_aigents.data_ingestion.db.postgres_db import PostgresDB


class FinancialDB(PostgresDB):
    def get_prices(
        self,
        ticker: str | list[str],
        start_date: datetime.datetime,
        end_date: datetime.datetime,
    ) -> pd.DataFrame:
        if isinstance(ticker, str):
            ticker_condition = "ticker = :ticker"
            params = {"ticker": ticker, "start_date": start_date, "end_date": end_date}
        else:
            ticker_condition = "ticker IN :ticker"
            params = {
                "ticker": tuple(ticker),
                "start_date": start_date,
                "end_date": end_date,
            }

        return pd.read_sql(
            text(
                f"SELECT * FROM stock_price_daily WHERE {ticker_condition} AND date BETWEEN :start_date AND :end_date"
            ),
            self.engine,
            params=params,
        )

    def get_top_volume_tickers(self, top_n: int | None = 100) -> pd.DataFrame:
        limit = ""
        if top_n:
            limit = f"WHERE top_n <= {top_n}"

        # return pd.read_sql(
        #    f"""
        #    SELECT *, Row_number()OVER() as top_n
        #    FROM (
        #        SELECT ticker, max(close * volume) as daily_volume FROM ticker_prices WHERE close is not null GROUP BY 1 ORDER BY daily_volume DESC {limit}
        #    ) a
        #    """,
        #    self.engine,
        # )["ticker"].to_list()
        return pd.read_sql(
            f"""
            SELECT *
            FROM volume_tickers
            {limit}
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
            text("SELECT ticker FROM active_tickers WHERE created_at = :filter_date"),
            self.engine,
            params={"filter_date": date},
        )["ticker"].to_list()
