import os
from src.data_ingestion.db.postgres_db import PostgresConfig, PostgresDB
from src.data_ingestion.downloader.yahoo_ticker_downloader import YahooTickerDownloader


if __name__ == "__main__":
    downloader = YahooTickerDownloader()
    stats = downloader.download_ticker_stats(["AAPL"])

    db_config = PostgresConfig(
        host=os.environ["SB_DDBB_HOST"],
        port=os.environ["SB_DDBB_PORT"],
        database=os.environ["SB_DDBB_DATABASE"],
        user=os.environ["SB_DDBB_USER"],
        password=os.environ["SB_DDBB_PWD"]
    )

    db = PostgresDB(config=db_config)

    stats.to_sql("stock_stats", db.engine, if_exists='append', index=False)
