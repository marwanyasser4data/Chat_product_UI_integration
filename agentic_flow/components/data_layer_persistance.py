from utils.sqlite_schema import SCHEMA_DDL
from local_storage import assert_local_data_layer_engine
from chainlit.data.sql_alchemy import SQLAlchemyDataLayer
from typing import Literal


def get_local_data_layer():
    engine = assert_local_data_layer_engine()
    async_location = str(engine.url).replace('sqlite','sqlite+aiosqlite')
    _data_layer = SQLAlchemyDataLayer(conninfo=async_location)
    return _data_layer


def get_data_layer(type: Literal['on_disk', 'memory'] ):
    if type == 'on_disk':
        return get_local_data_layer()

chainlit_data_layer = get_data_layer('on_disk')