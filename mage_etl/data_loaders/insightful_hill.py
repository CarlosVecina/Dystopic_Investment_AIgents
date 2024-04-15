from mage_ai.settings.repo import get_repo_path
from mage_ai.io.config import ConfigFileLoader
from mage_ai.io.google_cloud_storage import GoogleCloudStorage
from os import path
if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test
import os
import pandas as pd

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/src/keys/my_creds.json"


@data_loader
def load_from_google_cloud_storage(*args, **kwargs):
    """
    Template for loading data from a Google Cloud Storage bucket.
    Specify your configuration settings in 'io_config.yaml'.

    Docs: https://docs.mage.ai/design/data-loading#googlecloudstorage
    """


    bucket_name = 'terraform-demo-20240115-demo-bucket'
    object_key = 'fhv/*'

    gcs = GoogleCloudStorage()

    pq_file = gcs.load(
        bucket_name=bucket_name,
        object_key=object_key,
        format="Parquet"
    )

    print(pq_file)

    return pq_file


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
