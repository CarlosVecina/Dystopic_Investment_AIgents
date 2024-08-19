import argparse
import os
import sys
from functools import partial

from dystopic_investment_aigents.data_ingestion.db.financial_db import (
    FinancialDB,
)
from dystopic_investment_aigents.data_ingestion.db.postgres_db import (
    PostgresConfig,
)
from dystopic_investment_aigents.data_ingestion.downloader.yahoo_ticker_downloader import (
    YahooTickerDownloader,
)

if __name__ == "__main__":
    db_config = PostgresConfig(
        host=os.environ["SB_DDBB_HOST"],
        port=os.environ["SB_DDBB_PORT"],
        database=os.environ["SB_DDBB_DATABASE"],
        user=os.environ["SB_DDBB_USER"],
        password=os.environ["SB_DDBB_PWD"],
    )

    db = FinancialDB(config=db_config)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--top_n", help="All tickers or just the top ones", default=400
    )
    parser.add_argument(
        "--dry-run", help="Keep or not in the database", default=False
    )
    args = parser.parse_args()

    downloader = YahooTickerDownloader(db=db)
    tickers = downloader.get_all_tickers(args.top_n)
    df_news = downloader.download_ticker_news(tickers).drop_duplicates("uuid")

    if args.dry_run:
        print(df_news)
        sys.exit("Dry run")

    df_news.to_sql(
        "news_yh",
        db.engine,
        if_exists="append",
        method=partial(db.insert_on_conflict_nothing, index_elements=["uuid"]),
        index=False,
    )
