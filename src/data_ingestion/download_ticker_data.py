
import argparse
from typing import Any
import datetime
from pandas import DataFrame
import os
import json
import requests
import pandas as pd

import vectorbt as vbt
from dotenv import load_dotenv
import ssl

from src.data_ingestion.db.postgres_db import PostgresConfig, PostgresDB
from src.data_ingestion.downloader.yahoo_ticker_downloader import YahooTickerDownloader

load_dotenv()
sslcontext = ssl._create_unverified_context()

def get_all_tickers(only_top_marketcap: bool = False) -> list[Any]:
    if only_top_marketcap:
        return [
            "MSFT", "AAPL", "NVDA", "GOOGL", "AMZN", "META", "BRK.B", "LLY", "TSM", "AVGO",
            "NVO", "V", "TSLA", "JPM", "WMT", "XOM", "MA", "UNH", "ASML", "PG", "JNJ", "HD",
            "ORCL", "TM", "COST", "MRK", "CVX", "ABBV", "CRM", "BAC", "NFLX", "AMD", "KO",
            "SHEL", "PEP", "TMO", "LIN", "ADBE", "AZN", "SAP", "DIS", "WFC", "ACN", "CSCO",
            "MCD", "BABA", "QCOM", "TMUS", "ABT", "NVS", "CAT", "DHR", "INTU", "AMAT", "GE",
            "TTE", "IBM", "VZ", "AXP", "NOW", "UBER", "CMCSA", "COP", "HSBC", "PDD", "TXN",
            "INTC", "BX", "BHP", "PFE", "AMGN", "UNP", "MS", "NKE", "RY", "PM", "HDB", "ISRG",
            "MU", "SPGI", "RTX", "LOW", "SYK", "ARM", "NEE", "HON", "ETN", "GS", "LRCX", "SCHW",
            "UPS", "BKNG", "BUD", "PGR", "MUFG", "UL", "T", "ELV", "C", "BLK", "RIO", "DE",
            "PLD", "BP", "LMT", "TJX", "SNY", "MDT", "BA", "ABNB", "VRTX", "SONY", "CI", "PBR",
            "TD", "ADP", "BSX", "CB", "PBR.A", "BMY", "REGN", "MMC", "SBUX", "ADI", "UBS", "PANW",
            "SHOP", "MDLZ", "FI", "SCCO", "CVS", "KKR", "HCA", "SNPS", "GILD", "CNQ", "ANET",
            "DELL", "EQNR", "AMT", "CDNS", "GSK", "WM", "CNI", "CMG", "SHW", "CP", "GD", "EOG",
            "RELX", "STLA", "TGT", "SMFG", "DEO", "ITW", "CME", "MPC", "SO", "ICE", "CRWD", "RACE",
            "SLB", "INFY", "MELI", "DUK", "MAR", "ENB", "MO", "EQIX", "SAN", "FCX", "CL", "PH",
            "PSX", "CSX", "WDAY", "MCO", "TRI", "MCK", "ZTS", "PYPL", "APH", "BDX", "TDG", "ROP",
            "MSI", "MNST", "CRH", "AMX", "DASH", "NSC", "EW", "E", "TEAM", "COIN", "RSG", "BNS",
            "SPOT", "NTES", "VLO", "ITUB", "ROP", "CEG", "PNC", "NXPI", "COIN", "RSG", "BNS",
            "SPOT", "NTES", "VLO", "ITUB", "PCAR", "HMC", "BBVA", "OXY", "AON", "MRVL", "CEG",
            "PNC", "CPRT", "SNOW", "NU", "SMCI", "DXCM", "ING", "ET", "HLT"
        ]
    else:

        url = "https://paper-api.alpaca.markets/v2/assets?status=active&exchange=NASDAQ&attributes=options_enabled"
    
        headers = {
            "accept": "application/json",
            "APCA-API-KEY-ID": os.environ["APCA_API_KEY_ID"],
            "APCA-API-SECRET-KEY": os.environ["APCA_API_SECRET_KEY"],
        }
        response = requests.get(url, headers=headers)
        response_parsed = json.loads(response.text)  
    
        symbol_list = list()
        for i in response_parsed:
            symbol_list.append(i["symbol"])
        
        return symbol_list


def download_ticker_data(tickers: str | list[str], start_date: datetime.datetime, end_date: datetime.datetime) -> DataFrame:
    if isinstance(tickers, str):
        return vbt.AlpacaData.download_symbol(tickers, start=start_date, end=end_date)

    response_dict = dict()
    for symbol in tickers:
        response_dict[symbol] = vbt.AlpacaData.download_symbol(symbol, start=start_date, end=end_date)
    return response_dict


if __name__ == "__main__":
    parser=argparse.ArgumentParser()

    parser.add_argument("--start_date", help="Start date to download data")
    parser.add_argument("--end_date", help="End date to download data")
    parser.add_argument("--all", help="All tickers or just the top ones", default=True)

    args=parser.parse_args()

    end_data = datetime.datetime.now().date().strftime("%Y-%m-%d")
    start_date = (datetime.datetime.now().date() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    if args.start_date and args.end_date:
        end_data = args.end_date
        start_date = args.start_date

    #tickers_price = download_ticker_data(
    #    tickers=tickers, 
    #    start_date=args.start_date, 
    #    end_date=args.end_date
    #)
    ticker_downloader = YahooTickerDownloader()
    
    tickers = ticker_downloader.get_all_tickers(args.all)

    tickers_price = ticker_downloader.download_ticker_data(
        tickers=tickers, 
        start_date=args.start_date, 
        end_date=args.end_date,
    )

    db_config = PostgresConfig(
        host=os.environ["SB_DDBB_HOST"],
        port=os.environ["SB_DDBB_PORT"],
        database=os.environ["SB_DDBB_DATABASE"],
        user=os.environ["SB_DDBB_USER"],
        password=os.environ["SB_DDBB_PWD"]
    )

    db = PostgresDB(config=db_config)


    tickers_price.to_sql("stock_price_daily", db.engine, if_exists='append', index=False)

