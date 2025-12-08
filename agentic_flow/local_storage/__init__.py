import os
from sqlalchemy import create_engine, text
import sqlalchemy
from utils.sqlite_schema import SCHEMA_DDL
from utils.chainlit_logger import log_info, log_warning

DATA_PATH = os.path.dirname(__file__)

def assert_local_data_layer_engine() -> sqlalchemy.engine.Engine:
    engine = create_engine(
            f"sqlite:///{os.path.join(DATA_PATH,'data_layer.db')}",
            future=True,)
    with engine.begin() as conn:
        for statement in SCHEMA_DDL.split(';'):
            if statement != '\n':
                conn.execute(text(statement))

    return engine

def get_local_credentials_db_path() -> str:
    return os.path.join(DATA_PATH, 'credentials_db')


def get_local_checkpointer_path() -> str:
    return os.path.join(DATA_PATH,'langgraph_checkpointer.db')


def get_local_real_estate_mcp_path() -> str:
    return os.path.join(DATA_PATH, "real_estate_sales_mcp.py")


def get_local_real_estate_db_path() -> str:
    return DATA_PATH

def get_local_real_estate_data() -> str:
    return os.path.join(DATA_PATH, 'bayut_selling_properties_ksa.csv')