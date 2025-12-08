from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from local_storage import get_local_checkpointer_path
import aiosqlite
from typing import Literal
import asyncio

'''
    Can use checkpointer based on database like postgres, MongoDB, Redis
    Also on disk (local)

'''
in_memory_checkpointer = InMemorySaver()


on_disk_checkpointer_name = get_local_checkpointer_path()


async def get_checkpointer(type: Literal['on_disk_sqlite', 'memory']):

    if type == 'on_disk_sqlite':
        # Create persistent connection with multi-user settings
        _sqlite_conn = await aiosqlite.connect(
            on_disk_checkpointer_name,
            check_same_thread=False,  
        )
        
        # Enable WAL mode for concurrent reads/writes
        await _sqlite_conn.execute("PRAGMA journal_mode=WAL")
        
        # Create SqliteSaver with persistent connection
        _checkpointer = AsyncSqliteSaver(_sqlite_conn)
        
        # Initialize tables
        await _checkpointer.setup()

        return _checkpointer
    
    elif type == 'memory':
        return in_memory_checkpointer
    
checkpointer = asyncio.run(get_checkpointer(type='on_disk_sqlite'))