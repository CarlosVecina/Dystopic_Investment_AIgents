from pydantic import BaseModel
from adalflow import PostgresRetriever


class NewsRetriever(BaseModel, PostgresRetriever):
    pass