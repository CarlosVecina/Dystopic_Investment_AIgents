import datetime
from pydantic import BaseModel
import yfinance as yf
import pandas as pd

from dystopic_investment_aigents.data_ingestion.db.financial_db import FinancialDB
from dystopic_investment_aigents.utils.parse_utils import camel_case_to_snake_case

class YahooTickerDownloader(BaseModel):
    db: FinancialDB | None = None

    class Config:
        arbitrary_types_allowed = True
    
    def get_all_tickers(self, top_n: int):
        return self.db.get_top_volume_tickers(top_n)

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
    
    def download_ticker_news(self, tickers: list[str]) -> pd.DataFrame:
        result = pd.DataFrame()
        for ticker in tickers:
            try:
                tt = yf.Ticker(ticker)
                ticker_news = pd.DataFrame(tt.news)
                ticker_news["ticker"] = ticker
                result = pd.concat([result, ticker_news], ignore_index=True)
            except Exception as e:
                print(e)
                pass

        result.columns = [camel_case_to_snake_case(col_name) for col_name in result.columns]        
        result["created_at"] = datetime.datetime.now()
        #TODO: best format for this?
        #result["related_tickers"] = result["related_tickers"].apply(lambda x: ", ".join(x))

        news_columns = ['uuid', 'ticker', 'title', 'publisher', 'link', 'provider_publish_time', 'related_tickers', 'created_at']
        return result[news_columns]
    
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
                df_ticker_info["date"] = datetime.datetime.now().date()
                df_info = pd.concat([df_info, df_ticker_info])
            except:
                print(f"Error downloading {ticker}")
            
        return df_info