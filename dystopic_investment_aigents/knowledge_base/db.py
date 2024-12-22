from sqlalchemy import create_engine
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()

class PostgresConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SB_DDBB_")
    host: str
    port: str
    database: str
    user: str
    password: str

    def get_connection_string(self) -> str:
        return f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


db_uri = PostgresConfig().get_connection_string()

supabase_engine = create_engine(db_uri)
