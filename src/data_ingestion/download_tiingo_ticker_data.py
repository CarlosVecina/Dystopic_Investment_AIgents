import argparse
import datetime
import os

from src.data_ingestion.db.postgres_db import PostgresConfig, PostgresDB
from src.data_ingestion.downloader.tiingo_ticker_downloader import (
    TiingoDownloader,
)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--date", help="Dily data date", required=False)

    args = parser.parse_args()

    db_config = PostgresConfig(
        host=os.environ["SB_DDBB_HOST"],
        port=os.environ["SB_DDBB_PORT"],
        database=os.environ["SB_DDBB_DATABASE"],
        user=os.environ["SB_DDBB_USER"],
        password=os.environ["SB_DDBB_PWD"],
    )
    db = PostgresDB(config=db_config)

    dwn = TiingoDownloader(engine=db.engine)
    tickers = dwn.available_tickers(date=None)

    tickers = tickers[1900:]

    date = datetime.datetime.now() - datetime.timedelta(days=1)
    if args.date:
        date = args.date

    print(f"Downloading data for date {date}")

    df = dwn.get_daily_prices(tickers, date)
    df.to_sql("ticker_prices", db.engine, if_exists="append", index=False)
