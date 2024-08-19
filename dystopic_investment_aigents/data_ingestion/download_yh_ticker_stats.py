import os

from dystopic_investment_aigents.data_ingestion.db.financial_db import FinancialDB
from dystopic_investment_aigents.data_ingestion.db.postgres_db import \
    PostgresConfig
from dystopic_investment_aigents.data_ingestion.downloader.yahoo_ticker_downloader import YahooTickerDownloader


if __name__ == "__main__":
    db_config = PostgresConfig(
        host=os.environ["SB_DDBB_HOST"],
        port=os.environ["SB_DDBB_PORT"],
        database=os.environ["SB_DDBB_DATABASE"],
        user=os.environ["SB_DDBB_USER"],
        password=os.environ["SB_DDBB_PWD"]
    )
    db = FinancialDB(config=db_config)
    tickers = db.get_top_volume_tickers(1000)

    downloader = YahooTickerDownloader()
    stats = downloader.download_ticker_stats(tickers)

    stats.to_sql("stock_stats", db.engine, if_exists='append', index=False)
