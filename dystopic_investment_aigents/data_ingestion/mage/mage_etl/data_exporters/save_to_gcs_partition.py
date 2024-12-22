import os

import pyarrow as pa
import pyarrow.parquet as pq

if "data_exporter" not in globals():
    from mage_ai.data_preparation.decorators import data_exporter

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = (
    "/home/dystopic_investment_aigents/keys/my_creds.json"
)

bucket_name = "terraform-demo-20240115-demo-bucket"
project_id = "concise-quarter-411516"

table_name = "ticker_daily_prices"

root_path = f"{bucket_name}/{table_name}"


@data_exporter
def export_data(data, *args, **kwargs):
    """
    Exports data to some source.

    Args:
        data: The output from the upstream parent block
        args: The output from any additional upstream blocks (if applicable)

    Output (optional):
        Optionally return any object and it'll be logged and
        displayed when inspecting the block run.
    """

    data["timestamp"] = data["timestamp"].dt.date

    table = pa.Table.from_pandas(data)

    gcs = pa.fs.GcsFileSystem()

    pq.write_to_dataset(
        table,
        root_path=root_path,
        partition_cols=["timestamp"],
        filesystem=gcs,
        # existing_data_behavior="delete_matching"
    )
