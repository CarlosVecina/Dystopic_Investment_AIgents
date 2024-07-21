import datetime
from dotenv import load_dotenv
import pandas as pd
from pydantic import BaseModel
import requests
from sqlalchemy import Engine, text
import os

load_dotenv()

TIINGO_API = os.environ["TIINGO_API"]


class TiingoDownloader(BaseModel):
    engine: Engine

    class Config:
        arbitrary_types_allowed = True

    # TODO: Decouple db logic from the downloader
    def available_tickers(
        self, date: datetime.datetime | None
    ) -> list[str] | None:
        if not date:
            date = pd.read_sql(
                text("SELECT max(created_at) FROM active_tickers"), self.engine
            )["max"].to_list()[0]

        return pd.read_sql(
            text(
                "SELECT ticker FROM active_tickers WHERE created_at = :filter_date"
            ),
            self.engine,
            params={"filter_date": date},
        )

    def get_prices(
        self,
        tickers: list[str],
        start_date: datetime.datetime,
        end_date: datetime.datetime = datetime.datetime.now(),
    ) -> pd.DataFrame:
        headers = {"Content-Type": "application/json"}
        df_tickers = pd.DataFrame()
        for ticker in tickers:
            response = requests.get(
                f"https://api.tiingo.com/tiingo/daily/{ticker}/prices?token={TIINGO_API}&startDate={start_date.date()}&endDate={end_date.date()}",
                headers=headers,
            ).json()
            response["ticker"] = ticker
            response["created_at"] = datetime.datetime.now()
            df_tickers = pd.concat([df_tickers, pd.DataFrame(response)])
        return df_tickers

    def get_daily_prices(
        self, tickers: list[str], date: datetime.datetime
    ) -> pd.DataFrame:
        return self.get_prices(
            tickers, date, end_date=date + datetime.timedelta(days=1)
        )

    def _get_news_raw(
        self,
        tickers: str,
        start_date: datetime.datetime,
        end_date: datetime.datetime = datetime.datetime.now(),
        limit: int = 100,
    ) -> pd.DataFrame:
        """Aimed to be used internally to get news from Tiingo API"""
        headers = {"Content-Type": "application/json"}
        response = requests.get(
            f"https://api.tiingo.com/tiingo/news?token={TIINGO_API}&tickers={tickers}&startDate={start_date.date()}&endDate={end_date.date()}&limit={limit}",
            headers=headers,
        ).json()
        df_response = pd.DataFrame(response)
        df_response["created_at"] = datetime.datetime.now()
        return df_response

    def get_news(
        self,
        tickers: list[str],
        start_date: datetime.datetime,
        end_date: datetime.datetime = datetime.datetime.now(),
        limit_per_ticker: int = 100,
    ) -> pd.DataFrame:
        """Exposed method to get news from Tiingo API for multiple tickers iterating over each ticker thus several API calls.
        Note that here the limit is per ticker. So you may expect a final DF with shape[0] in (0, limit_per_ticker*len(tickers)] range.
        """
        df_tickers = pd.DataFrame()
        for query_ticker in tickers:
            df_response = self._get_news_raw(
                query_ticker, start_date, end_date, limit_per_ticker
            )
            df_tickers = pd.concat([df_tickers, df_response])

        return df_tickers

    def get_news_composed(
        self,
        tickers: list[str],
        start_date: datetime.datetime,
        end_date: datetime.datetime = datetime.datetime.now(),
        limit: int = 500,
    ) -> pd.DataFrame:
        """Exposed method to get news from Tiingo API for multiple tickers in the same API call.
        Note that here the limit is global, not per ticker. So you may expect a final with shape[0] in (0, limit] tange.
        """
        query_ticker = ",".join(tickers)
        df_response = self._get_news_raw(
            query_ticker, start_date, end_date, limit
        )

        return df_response

    def get_daily_news_composed(
        self,
        tickers: list[str],
        date: datetime.datetime,
        limit: int = 500,
    ) -> pd.DataFrame:
        return self.get_news_composed(
            tickers=tickers,
            start_date=date,
            end_date=date + datetime.timedelta(days=1),
            limit=limit,
        )
