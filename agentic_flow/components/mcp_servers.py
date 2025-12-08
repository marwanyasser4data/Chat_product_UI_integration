import subprocess 
import docker
import sys
from typing import Literal, Optional
from pydantic import BaseModel
from utils.chainlit_logger import log_info, log_warning
from local_storage import ( get_local_real_estate_db_path,
                           get_local_real_estate_mcp_path)
from utils.populate_real_estate_db import main as synthasize_real_estate_db


class mcpServerConfigs(BaseModel):
    name: str
    transport: Literal['streamable_http', 'stdio']
    url: str # Either remote or localhost
    port: int 
    command: Optional[str] = None # Ex. 'python' if stdio for local file 
    args: Optional[list[str]] = None # path of the local script to run (if stdio)
    

mcp_process = None

def get_localhost_real_estate_mcp() -> mcpServerConfigs:
    global mcp_process
    script_path = get_local_real_estate_mcp_path()


    # Database running part
    def ensure_postgres_running():
        client = docker.from_env()
        fresh_db = False
        try:
            container = client.containers.get("real_estate_postgres")
            if container.status != "running":
                log_info("Postgres container exists but not running. Starting...")
                container.start()
                log_info("Postgres started.")
            else:
                log_info("Postgres is already running.")
        except docker.errors.NotFound:
            fresh_db = True
            log_info("Postgres container not found. Starting via docker compose...")
            import subprocess
            subprocess.run(
                ["docker", "compose", "up", "-d", "real_estate_postgres"],
                cwd=get_local_real_estate_db_path(),
                check=True
            )
            log_info("Postgres started.")

        # Optional: block until healthy
        log_info("Waiting for Postgres to be ready...")
        try:
            _wait_for_health(client, "real_estate_postgres")
            if fresh_db: synthasize_real_estate_db(); log_info('Populating database with synthetic data...')
        except Exception as e:
            print(f' Error when initiating DB: {e}')

    def _wait_for_health(client, name):
        import time
        for _ in range(30):
            container = client.containers.get(name)
            if container.attrs["State"].get("Health", {}).get("Status") == "healthy":
                log_info("Postgres is healthy.")
                return
            time.sleep(1)
        log_warning("WARNING: Postgres never reached healthy state.")
        raise Exception('Database never reached healthy state ')

    try:
        ensure_postgres_running()
        # MCP server running part
        port = 3002
        mcp_process = subprocess.Popen(
            [sys.executable, script_path, str(port)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL)
        if mcp_process.poll() is None:

            log_info(f'MCP Server is running locally on port {port}...')
            return mcpServerConfigs(name='real_estate_sales', 
                                transport='streamable_http', 
                                url=f'http://localhost:{port}/mcp',
                                port=port)
        else:
            log_warning('MCP Server failed to run !')
            return None

        
    except Exception as e:
        print(f'Failed to run MCP with error: {e}')
        return None
    

