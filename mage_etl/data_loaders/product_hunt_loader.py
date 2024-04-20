if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test
from src.data_ingestion.download_product_hunt import fetch_ph_posts


@data_loader
def load_data(*args, **kwargs):

    response = fetch_ph_posts(10)

    return response


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
