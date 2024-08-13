import datetime
from pydantic import BaseModel
import yfinance as yf
import pandas as pd

from src.data_ingestion.db.postgres_db import FinancialDB

class YahooTickerDownloader(BaseModel):
    db: FinancialDB | None = None

    class Config:
        arbitrary_types_allowed = True
    
    def get_all_tickers(self, only_top_marketcap: bool = True):
        if only_top_marketcap:
            return self.db.get_top_volume_tickers(200)
            #return [
            #    "MSFT", "AAPL", "NVDA", "GOOGL", "AMZN", "META", "LLY", "TSM", "AVGO",
            #    "NVO", "V", "TSLA", "JPM", "WMT", "XOM", "MA", "UNH", "ASML", "PG", "JNJ", "HD",
            #    "ORCL", "TM", "COST", "MRK", "CVX", "ABBV", "CRM", "BAC", "NFLX", "AMD", "KO",
            #    "SHEL", "PEP", "TMO", "LIN", "ADBE", "AZN", "SAP", "DIS", "WFC", "ACN", "CSCO",
            #    "MCD", "BABA", "QCOM", "TMUS", "ABT", "NVS", "CAT", "DHR", "INTU", "AMAT", "GE",
            #    "TTE", "IBM", "VZ", "AXP", "NOW", "UBER", "CMCSA", "COP", "HSBC", "PDD", "TXN",
            #    "INTC", "BX", "BHP", "PFE", "AMGN", "UNP", "MS", "NKE", "RY", "PM", "HDB", "ISRG",
            #    "MU", "SPGI", "RTX", "LOW", "SYK", "ARM", "NEE", "HON", "ETN", "GS", "LRCX", "SCHW",
            #    "UPS", "BKNG", "BUD", "PGR", "MUFG", "UL", "T", "ELV", "C", "BLK", "RIO", "DE",
            #    "PLD", "BP", "LMT", "TJX", "SNY", "MDT", "BA", "ABNB", "VRTX", "SONY", "CI", "PBR",
            #    "TD", "ADP", "BSX", "CB", "BMY", "REGN", "MMC", "SBUX", "ADI", "UBS", "PANW",
            #    "SHOP", "MDLZ", "FI", "SCCO", "CVS", "KKR", "HCA", "SNPS", "GILD", "CNQ", "ANET",
            #    "DELL", "EQNR", "AMT", "CDNS", "GSK", "WM", "CNI", "CMG", "SHW", "CP", "GD", "EOG",
            #    "RELX", "STLA", "TGT", "SMFG", "DEO", "ITW", "CME", "MPC", "SO", "ICE", "CRWD", "RACE",
            #    "SLB", "INFY", "MELI", "DUK", "MAR", "ENB", "MO", "EQIX", "SAN", "FCX", "CL", "PH",
            #    "PSX", "CSX", "WDAY", "MCO", "TRI", "MCK", "ZTS", "PYPL", "APH", "BDX", "TDG", "ROP",
            #    "MSI", "MNST", "CRH", "AMX", "DASH", "NSC", "EW", "E", "TEAM", "COIN", "RSG", "BNS",
            #    "SPOT", "NTES", "VLO", "ITUB", "ROP", "CEG", "PNC", "NXPI", "COIN", "RSG", "BNS",
            #    "SPOT", "NTES", "VLO", "ITUB", "PCAR", "HMC", "BBVA", "OXY", "AON", "MRVL", "CEG",
            #    "PNC", "CPRT", "SNOW", "NU", "SMCI", "DXCM", "ING", "ET", "HLT"
            #]
        else:
            raise ValueError("Not implemented")

    def download_ticker_data(self, tickers: list[str], start_date: datetime.datetime, end_date: datetime.datetime) -> pd.DataFrame:
        if len(tickers) == 1:
            ticker = yf.Ticker(" ".join(tickers))
            result = ticker.history(start=start_date, end=end_date)
            result.reset_index(inplace=True)
            result["ticker"] = " ".join(tickers)
        else:
            ticker = yf.Tickers(" ".join(tickers))
            hist = ticker.history(start=start_date, end=end_date)

            tickers_data = []
            for ticker, data in hist.groupby(level=1, axis=1):
                data.columns = data.columns.droplevel(1)
                data.reset_index(inplace=True)
                data.insert(0, 'ticker', ticker)
                tickers_data.append(data)

            result = pd.concat(tickers_data[0:])

        ticker_columns = ["date", "ticker", "created_at", "open", "high", "low", "close", "dividends", "stock_splits", "volume"]

        if result.empty:
            return pd.DataFrame(columns=ticker_columns)

        result.columns = result.columns.str.lower().str.replace(" ", "_")
        result["created_at"] = datetime.datetime.now()

        return result[ticker_columns]
    
    def download_ticker_news(self, tickers: list[str], start_date: datetime.datetime, end_date: datetime.datetime):
        if len(tickers) == 1:
            ticker = yf.Ticker(" ".join(tickers))
            breakpoint()
            yf.utils.get_news_by_isin
            ticker_news = ticker.news
            ticker_news[0]
            result = ticker.history(start=start_date, end=end_date)
            result.reset_index(inplace=True)
            result["ticker"] = " ".join(tickers)
        else:
            ticker = yf.Tickers(" ".join(tickers))
            hist = ticker.history(start=start_date, end=end_date)

            tickers_data = []
            for ticker, data in hist.groupby(level=1, axis=1):
                data.columns = data.columns.droplevel(1)
                data.reset_index(inplace=True)
                data.insert(0, 'ticker', ticker)
                tickers_data.append(data)

            result = pd.concat(tickers_data[1:])

        result.columns = result.columns.str.lower().str.replace(" ", "_")
        result["created_at"] = datetime.datetime.now()

        ticker_columns = ["date", "ticker", "created_at", "open", "high", "low", "close", "dividends", "stock_splits", "volume"]
        return result[ticker_columns]
    
    def download_ticker_stats(self, tickers: list[str]):
        df_info = pd.DataFrame()

        fields = [
            'industryKey','sectorKey','fullTimeEmployees','auditRisk', 'boardRisk', 'compensationRisk', 'shareHolderRightsRisk',
            'overallRisk', 'governanceEpochDate', 'compensationAsOfEpochDate', 'irWebsite', 'maxAge', 'priceHint', 'previousClose', 
            'open', 'dayLow', 'dayHigh', 'regularMarketPreviousClose', 'regularMarketOpen', 'regularMarketDayLow', 'regularMarketDayHigh', 
            'dividendRate', 'dividendYield', 'exDividendDate', 'payoutRatio', 'fiveYearAvgDividendYield', 'beta', 'trailingPE', 'forwardPE', 
            'volume', 'regularMarketVolume', 'averageVolume', 'averageVolume10days', 'averageDailyVolume10Day', 'bid', 'ask', 'bidSize', 
            'askSize', 'marketCap', 'fiftyTwoWeekLow', 'fiftyTwoWeekHigh', 'priceToSalesTrailing12Months', 'fiftyDayAverage', 'twoHundredDayAverage',
            'trailingAnnualDividendRate', 'trailingAnnualDividendYield', 'currency', 'enterpriseValue', 'profitMargins', 'floatShares', 'sharesOutstanding', 
            'sharesShort', 'sharesShortPriorMonth', 'sharesShortPreviousMonthDate', 'dateShortInterest', 'sharesPercentSharesOut', 'heldPercentInsiders', 
            'heldPercentInstitutions', 'shortRatio', 'shortPercentOfFloat', 'impliedSharesOutstanding', 'bookValue', 'priceToBook', 'lastFiscalYearEnd', 
            'nextFiscalYearEnd', 'mostRecentQuarter', 'earningsQuarterlyGrowth', 'netIncomeToCommon', 'trailingEps', 'forwardEps', 'pegRatio', 'lastSplitFactor',
            'lastSplitDate', 'enterpriseToRevenue', 'enterpriseToEbitda', '52WeekChange', 'SandP52WeekChange', 'lastDividendValue', 'lastDividendDate', 'exchange',
            'quoteType', 'symbol', 'underlyingSymbol', 'shortName', 'longName', 'firstTradeDateEpochUtc', 'timeZoneFullName', 'timeZoneShortName', 'uuid', 
            'messageBoardId', 'gmtOffSetMilliseconds', 'currentPrice', 'targetHighPrice', 'targetLowPrice', 'targetMeanPrice', 'targetMedianPrice', 'recommendationMean',
            'recommendationKey', 'numberOfAnalystOpinions', 'totalCash', 'totalCashPerShare', 'ebitda', 'totalDebt', 'quickRatio', 'currentRatio', 'totalRevenue', 
            'debtToEquity', 'revenuePerShare', 'returnOnAssets', 'returnOnEquity', 'freeCashflow', 'operatingCashflow', 'earningsGrowth', 'revenueGrowth', 'grossMargins',
            'ebitdaMargins', 'operatingMargins', 'financialCurrency', 'trailingPegRatio'
        ]

        for ticker in tickers:
            try:
                data = yf.Ticker(ticker).info
                df_ticker_info = pd.DataFrame({key: value for key, value in data.items() if key in fields}, index=[0])
                df_ticker_info["ticker"] = ticker
                df_info = pd.concat([df_info, df_ticker_info])
            except:
                print(f"Error downloading {ticker}")
            
        return df_info