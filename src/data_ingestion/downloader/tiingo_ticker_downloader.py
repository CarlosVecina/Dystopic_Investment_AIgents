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
        self, tickers: list[str], start_date: datetime.datetime, end_date: datetime.datetime = datetime.datetime.now()
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
        return self.get_prices(tickers, date, end_date=date + datetime.timedelta(days=1))