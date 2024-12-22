from adalflow import PostgresRetriever
from pydantic import BaseModel


class NewsRetriever(BaseModel, PostgresRetriever):
    pass
