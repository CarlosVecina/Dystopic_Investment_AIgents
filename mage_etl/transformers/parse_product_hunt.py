if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

import pandas as pd
from src.data_ingestion.download_product_hunt import parse_ph_response
import datetime

@transformer
def transform(data, *args, **kwargs):

    product_list = parse_ph_response(data)
    df = pd.DataFrame([i.dict() for i in product_list])
    df["timestamp"] = datetime.datetime.now()

    return df


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
