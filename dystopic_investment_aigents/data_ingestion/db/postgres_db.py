from sqlalchemy import MetaData, Table, create_engine
from sqlalchemy.dialects.postgresql import insert


class PostgresConfig:
    def __init__(self, host, port, database, user, password):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password

    def get_connection_string(self):
        return f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


class PostgresDB:
    def __init__(self, config: PostgresConfig):
        self.config = config
        self.engine = create_engine(self.config.get_connection_string())
        self.connection = self.engine.connect()
        self.metadata = MetaData()
        # self.metadata.reflect(self.engine)

    def query(self, query_string):
        return self.connection.execute(query_string)

    def insert(self, table_name, data):
        table = Table(table_name, self.metadata, autoload_with=self.engine)
        self.connection.execute(table.insert(), data)

    @classmethod
    def insert_on_conflict_nothing(cls, table, conn, keys, data_iter, index_elements):
        data = [dict(zip(keys, row)) for row in data_iter]
        stmt = (
            insert(table.table)
            .values(data)
            .on_conflict_do_nothing(index_elements=index_elements)
        )
        result = conn.execute(stmt)
        return result.rowcount
