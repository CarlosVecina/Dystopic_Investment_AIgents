import argparse
import datetime
import os
import ssl
import sys

from dotenv import load_dotenv

from dystopic_investment_aigents.data_ingestion.db.financial_db import \
    FinancialDB
from dystopic_investment_aigents.data_ingestion.db.postgres_db import \
    PostgresConfig
from dystopic_investment_aigents.data_ingestion.downloader.yahoo_ticker_downloader import \
    YahooTickerDownloader

load_dotenv()
sslcontext = ssl._create_unverified_context()


if __name__ == "__main__":
    parser=argparse.ArgumentParser()

    parser.add_argument("--start_date", help="Start date to download data")
    parser.add_argument("--end_date", help="End date to download data")
    parser.add_argument("--top_n", help="All tickers or just the top ones", default=400)
    parser.add_argument("--dry-run", help="Keep or not in the database", default=False)

    args=parser.parse_args()

    db_config = PostgresConfig(
        host=os.environ["SB_DDBB_HOST"],
        port=os.environ["SB_DDBB_PORT"],
        database=os.environ["SB_DDBB_DATABASE"],
        user=os.environ["SB_DDBB_USER"],
        password=os.environ["SB_DDBB_PWD"]
    )

    db = FinancialDB(config=db_config)

    # Time range to retrieve the data
    end_date = datetime.datetime.now().date().strftime("%Y-%m-%d")
    start_date = (datetime.datetime.now().date() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    if args.start_date:
        start_date = args.start_date
    
    if args.end_date:
        end_date = args.end_date

    ticker_downloader = YahooTickerDownloader(db=db)
    
    tickers = ticker_downloader.get_all_tickers(args.top_n)

    tickers_price = ticker_downloader.download_ticker_data(
        tickers=tickers, 
        start_date=start_date, 
        end_date=end_date,
    )
    
    if tickers_price.empty:
        sys.exit(f"No data to insert between {start_date} and {end_date}")

    if args.dry_run:
        print(tickers_price)
        sys.exit("Dry run")
    
    tickers_price.to_sql("stock_price_daily", db.engine, if_exists='append', index=False)
    
