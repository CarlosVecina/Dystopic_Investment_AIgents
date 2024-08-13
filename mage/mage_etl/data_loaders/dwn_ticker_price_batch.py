if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

from dystopic_investment_aigents.data_ingestion.download_yh_ticker_data import get_all_tickers, download_ticker_data

import json
import datetime
import pandas as pd

TOP_N = 50
START_DATE = datetime.datetime(2024, 1, 1)

@data_loader
def load_data(*args, **kwargs):
    """
    Template code for loading data from any source.

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """

    symbol_list = get_all_tickers(only_top_marketcap=True)
        
    symbol_list = symbol_list[:TOP_N]

    print(symbol_list)
    print(kwargs["execution_date"])
    print(kwargs["execution_date"] - datetime.timedelta(days=1))

    response_dict = download_ticker_data(
        tickers=symbol_list,
        start_date=START_DATE,
        end_date=kwargs["execution_date"] - datetime.timedelta(days=1)
    )

    df = pd.concat(response_dict, axis=0).reset_index(level=0).rename({'level_0':'ticker'}, axis=1).sort_index(ascending=False)

    return df.reset_index()


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
