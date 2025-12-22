import logging
import os
from typing import Any


import uvicorn
from sqlalchemy import create_engine, text


from mcp.server import Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
)


from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse, Response
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware


# -------------------------------------------------------
# Logging
# -------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("aml_postgres_mcp_server")


# -------------------------------------------------------
# DB engines
# -------------------------------------------------------
# SharedServices: standard Viya platform schemas
engine_shared = create_engine(
    "postgresql+psycopg2://postgres:Orion123@sasserver.demo.sas.com:5432/SharedServices",
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
)


# amlcore: holds AML core data, including schema `core`
engine_amlcore = create_engine(
    "postgresql+psycopg2://postgres:Orion123@sasserver.demo.sas.com:5432/amlcore",
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
)


# -------------------------------------------------------
# Allowed schemas
# -------------------------------------------------------
SAFE_SCHEMAS = [
    "fdhdata",
    "svivisualinvestigator",
    "svi_scorecard",
    "svidocumentgeneration",
    "svi_alerts",
    "core"
]


# -------------------------------------------------------
# Intent → schema mapping (for route_schema tool)
# -------------------------------------------------------
INTENT_TO_SCHEMA = {
    "case_investigation": ["fdhdata", "svi_alerts"],
    "alert_investigation": ["svi_alerts"],
    "party_customer": ["core", "fdhdata"],
    "account_analysis": ["core", "fdhdata"],
    "transaction_analysis": ["core"],
    "risk_scoring": ["svi_scorecard"],
    "regulatory_reporting": ["fdhdata"],
    "documents_narratives": ["svidocumentgeneration"],
    "visual_investigator_ui": ["svivisualinvestigator"],
    "audit_system": ["fdhdata", "svivisualinvestigator"]
}
# -------------------------------------------------------
# MCP server object
# -------------------------------------------------------
mcp_server = Server("aml_postgres_mcp_server")


# -------------------------------------------------------
# Helper functions (DB routing + logic)
# -------------------------------------------------------




def _get_engine_for_schema(schema: str):
    """
    Route to the correct DB engine based on schema name.


    - 'core'      → amlcore DB
    - everything else in SAFE_SCHEMAS → SharedServices DB
    """
    if schema == "core":
        return engine_amlcore
    return engine_shared





def _route_schema(intent: str) -> str:
    schemas = INTENT_TO_SCHEMA.get(intent.lower())
    if not schemas:
        return "No matching schema found for this intent."
    return ", ".join(schemas)




def _list_tables(schema: str) -> str:
    if schema not in SAFE_SCHEMAS:
        return f"Access denied: schema '{schema}' not allowed."


    eng = _get_engine_for_schema(schema)


    with eng.connect() as conn:
        result = conn.execute(
            text(
                """
                SELECT c.relname, obj_description(c.oid, 'pg_class')
                FROM pg_class c
                JOIN pg_namespace n ON n.oid = c.relnamespace
                WHERE c.relkind = 'r' AND n.nspname = :schema;
                """
            ),
            {"schema": schema},
        )
        rows = result.fetchall()


    if not rows:
        return f"No tables found in schema '{schema}'."


    out = [f"Tables in {schema}:"]
    for name, comment in rows:
        out.append(f"- {name} | {comment or '—'}")
    return "\n".join(out)





def _execute_query(sql: str) -> str:
    sql_lower = sql.lower()


    if not any(f"{schema}." in sql_lower for schema in SAFE_SCHEMAS):
        return "Error: query must reference at least one allowed schema."


    forbidden = [" insert ", " update ", " delete ", " drop ", " alter ", " truncate "]
    if any(word in sql_lower for word in forbidden):
        return "Error: only read-only SELECT queries are allowed."


    # Decide which engine to use:
    # If query references core. → amlcore
    # Otherwise → SharedServices
    if "core." in sql_lower:
        eng = engine_amlcore
    else:
        eng = engine_shared


    with eng.connect() as conn:
        result = conn.execute(text(sql))


        if not result.returns_rows:
            return "Query executed successfully (no rows returned)."


        rows = result.fetchall()
        headers = list(result.keys())


    out = [" | ".join(headers)]
    for r in rows[:20]:
        out.append(" | ".join(str(v) if v is not None else "NULL" for v in r))
    return "\n".join(out)




def _get_table_info(schema_name: str, table_name: str) -> str:
    if schema_name not in SAFE_SCHEMAS:
        return f"Access denied: schema '{schema_name}' not allowed."


    eng = _get_engine_for_schema(schema_name)


    with eng.connect() as conn:
        result = conn.execute(
            text(
                """
                SELECT
                    a.attname AS column_name,
                    pg_catalog.format_type(a.atttypid, a.atttypmod) AS data_type,
                    CASE WHEN a.attnotnull THEN 'NO' ELSE 'YES' END AS is_nullable,
                    pg_get_expr(ad.adbin, ad.adrelid) AS column_default,
                    d.description AS comment
                FROM pg_attribute a
                JOIN pg_class c ON a.attrelid = c.oid
                JOIN pg_namespace n ON n.oid = c.relnamespace
                LEFT JOIN pg_description d ON d.objoid = a.attrelid AND d.objsubid = a.attnum
                LEFT JOIN pg_attrdef ad ON a.attrelid = ad.adrelid AND a.attnum = ad.adnum
                WHERE n.nspname = :schema_name
                  AND c.relname = :table_name
                  AND a.attnum > 0
                  AND NOT a.attisdropped
                ORDER BY a.attnum;
                """
            ),
            {"schema_name": schema_name, "table_name": table_name},
        )
        rows = result.fetchall()


    if not rows:
        return f"No table found named {schema_name}.{table_name}"


    out = [f"Columns in {schema_name}.{table_name}:"]
    for row in rows:
        out.append(
            f"- {row.column_name} | {row.data_type} | "
            f"Nullable: {row.is_nullable} | "
            f"Default: {row.column_default} | "
            f"Comment: {row.comment or ''}"
        )
    return "\n".join(out)




def _get_schema_relationships(schema_name: str) -> str:
    if schema_name not in SAFE_SCHEMAS:
        return f"Access denied: schema '{schema_name}' not allowed."


    eng = _get_engine_for_schema(schema_name)


    try:
        with eng.connect() as conn:
            query = text(
                """
                SELECT
                    tc.table_schema,
                    tc.table_name,
                    kcu.column_name,
                    ccu.table_schema AS foreign_table_schema,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name,
                    tc.constraint_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY'
                  AND tc.table_schema = :schema
                ORDER BY tc.table_name, kcu.column_name;
                """
            )


            result = conn.execute(query, {"schema": schema_name})
            rows = result.fetchall()


        if not rows:
            return f"No relationships (foreign keys) found in schema '{schema_name}'."


        relationships = [f"Relationships in schema '{schema_name}':", ""]
        for row in rows:
            relationships.append(
                f"- {row.table_name}.{row.column_name} → "
                f"{row.foreign_table_name}.{row.foreign_column_name} "
                f"(constraint: {row.constraint_name})"
            )


        return "\n".join(relationships)


    except Exception as e:
        return f"Error fetching relationships: {str(e)}"




# -------------------------------------------------------
# MCP: tools
# -------------------------------------------------------




@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools for querying AML Postgres."""
    return [
        Tool(
            name="route_schema",
            description=(
                "Given a user intent or question type, return which schema(s) to use. "
                "Examples: 'alerts', 'workflow', 'risk_score', 'analytics', 'party', 'core', 'system', etc."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "intent": {
                        "type": "string",
                        "description":  "High-level AML intent, e.g. 'alerts', 'workflow', 'risk_score'.",
                    }
                },
                "required": ["intent"],
            },
        ),
        Tool(
            name="get_tables",
            description="Get table names and their comments for a selected safe schema.",
            inputSchema={
                "type": "object",
                "properties": {
                    "database_schema": {
                        "type": "string",
                        "description": "Schema name (must be in SAFE_SCHEMAS), e.g. 'svi_alerts' or 'core'.",
                    }
                },
                "required": ["database_schema"],
            },
        ),
        Tool(
            name="get_table_info",
            description="Get column details for a given table in a safe schema.",
            inputSchema={
                "type": "object",
                "properties": {
                    "schema_name": {
                        "type": "string",
                        "description": "Schema name, e.g. 'svi_alerts' or 'core'.",
                    },
                    "table_name": {
                        "type": "string",
                        "description": "Table name inside the schema.",
                    },
                },
                "required": ["schema_name", "table_name"],
            },
        ),
        Tool(
            name="execute_sql_query",
            description=(
                "Execute a read-only SQL SELECT query against the allowed PostgreSQL schemas. "
                "The query must reference at least one allowed schema."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "sql_query": {
                        "type": "string",
                        "description": "The SQL SELECT query to run (read-only).",
                    }
                },
                "required": ["sql_query"],
            },
        ),

        Tool(
            name="get_schema_relationships",
            description=(
                "Show table relationships (foreign keys and references) for a given schema."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "schema_name": {
                        "type": "string",
                        "description": "Schema name whose relationships you want to inspect.",
                    }
                },
                "required": ["schema_name"],
            },
        )
    ]




@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    logger.info(f"call_tool name={name}, arguments={arguments}")

    # 2) route_schema
    if name == "route_schema":
        intent = arguments.get("intent")
        if not intent:
            raise ValueError("Missing 'intent' argument.")
        result_text = _route_schema(intent)
        return [TextContent(type="text", text=result_text)]


    # 3) get_tables
    if name == "get_tables":
        database_schema = arguments.get("database_schema")
        if not database_schema:
            raise ValueError("Missing 'database_schema' argument.")
        result_text = _list_tables(database_schema)
        return [TextContent(type="text", text=result_text)]


    # 4) get_table_info
    if name == "get_table_info":
        schema_name = arguments.get("schema_name")
        table_name = arguments.get("table_name")
        if not schema_name or not table_name:
            raise ValueError("Missing 'schema_name' or 'table_name' argument.")
        result_text = _get_table_info(schema_name, table_name)
        return [TextContent(type="text", text=result_text)]


    # 5) execute_sql_query
    if name == "execute_sql_query":
        sql_query = arguments.get("sql_query")
        if not sql_query:
            raise ValueError("Missing 'sql_query' argument.")
        try:
            result_text = _execute_query(sql_query)
            return [TextContent(type="text", text=result_text)]
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return [TextContent(type="text", text=f"Error executing query: {e}")]




    # 8) get_schema_relationships
    if name == "get_schema_relationships":
        schema_name = arguments.get("schema_name")
        if not schema_name:
            raise ValueError("Missing 'schema_name' argument.")
        result_text = _get_schema_relationships(schema_name)
        return [TextContent(type="text", text=result_text)]


    # Unknown tool
    raise ValueError(f"Unknown tool: {name}")




# -------------------------------------------------------
# Resources (currently empty, but MCP requires handlers)
# -------------------------------------------------------




@mcp_server.list_resources()
async def list_resources() -> list[Resource]:
    """Return an empty list of resources (no file-like resources exposed yet)."""
    return []




# -------------------------------------------------------
# JSON-RPC handler for /mcp (HTTP)
# -------------------------------------------------------




async def mcp_http_handler(request):
    """
    Handle MCP JSON-RPC over HTTP POST.
    """
    try:
        body = await request.json()
        logger.info(f"Received MCP request: {body}")
    except Exception as e:
        return JSONResponse(
            {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {e}"},
            },
            status_code=400,
        )


    def no_body():
        r = Response(status_code=202)
        r.media_type = None
        return r


    # Batch support (optional)
    if isinstance(body, list):
        results = []
        any_requests = False
        for item in body:
            if isinstance(item, dict) and "id" in item:
                any_requests = True
            resp = await _handle_one(item)
            if resp is not None:
                results.append(resp)
        if not any_requests:
            return no_body()
        return JSONResponse(results)


    is_notification = isinstance(body, dict) and "id" not in body


    # MCP notification some clients send after initialize; ignore
    if body.get("method") == "notifications/initialized":
        return no_body()


    resp = await _handle_one(body)


    if is_notification:
        return no_body()


    if resp is None:
        return JSONResponse(
            {
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "error": {
                    "code": -32603,
                    "message": "Internal error: no response generated",
                },
            },
            status_code=500,
        )


    return JSONResponse(resp)




async def _handle_one(msg: dict) -> dict | None:
    """Dispatch MCP methods. Returns JSON-RPC response dict, or None for notifications."""
    if not isinstance(msg, dict):
        return {
            "jsonrpc": "2.0",
            "id": None,
            "error": {"code": -32600, "message": "Invalid Request"},
        }


    method = msg.get("method")
    params = msg.get("params", {}) or {}
    req_id = msg.get("id")
    is_notification = "id" not in msg


    try:
        # initialize
        if method == "initialize":
            if is_notification:
                return None
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2025-03-26",
                    "capabilities": {
                        "resources": {"subscribe": False, "listChanged": False},
                        "tools": {"listChanged": False},
                        "prompts": {"listChanged": False},
                    },
                    "serverInfo": {
                        "name": "aml_postgres_mcp_server",
                        "version": "1.0.0",
                    },
                },
            }


        # ping
        if method == "ping":
            if is_notification:
                return None
            return {"jsonrpc": "2.0", "id": req_id, "result": {}}


        # tools/list
        if method == "tools/list":
            if is_notification:
                return None
            tools_result = await list_tools()
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "tools": [
                        {
                            "name": t.name,
                            "description": t.description,
                            "inputSchema": t.inputSchema,
                        }
                        for t in tools_result
                    ]
                },
            }


        # tools/call
        if method == "tools/call":
            if is_notification:
                return None
            tool_name = params.get("name")
            tool_args = params.get("arguments", {}) or {}
            try:
                result = await call_tool(tool_name, tool_args)
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {"type": c.type, "text": c.text} for c in result
                        ],
                        "isError": False,
                    },
                }
            except Exception as e:
                logger.error(f"Tool execution error: {e}")
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": f"Error executing tool: {e}"}
                        ],
                        "isError": True,
                    },
                }


        # resources/list
        if method == "resources/list":
            if is_notification:
                return None
            resources_result = await list_resources()
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "resources": [
                        {
                            "uri": str(r.uri),
                            "name": r.name,
                            "mimeType": r.mimeType,
                            "description": r.description,
                        }
                        for r in resources_result
                    ]
                },
            }


        # unknown method
        if is_notification:
            return None


        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"},
        }


    except Exception as e:
        if is_notification:
            return None
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32603, "message": f"Internal error: {e}"},
        }




# -------------------------------------------------------
# Extra HTTP helpers
# -------------------------------------------------------




async def health_check(request):
    return JSONResponse(
        {
            "status": "healthy",
            "service": "AML Postgres MCP Server",
            "mcp_endpoint": "/mcp",
            "description": "Use POST requests to /mcp for MCP JSON-RPC calls",
        }
    )




async def test_tools(request):
    try:
        tools = await list_tools()
        return JSONResponse(
            {
                "available_tools": [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "inputSchema": tool.inputSchema,
                    }
                    for tool in tools
                ]
            }
        )
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)




# -------------------------------------------------------
# Starlette app
# -------------------------------------------------------
middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
]


app = Starlette(
    routes=[
        Route("/", health_check),
        Route("/health", health_check),
        Route("/mcp", mcp_http_handler, methods=["POST"]),
        Route("/tools", test_tools),
    ],
    middleware=middleware,
)


if __name__ == "__main__":
    port = int(os.getenv("AML_MCP_PORT", 4998))
    logger.info(f"Starting AML Postgres MCP server on port {port}...")
    logger.info(f"MCP HTTP endpoint: http://localhost:{port}/mcp")
    logger.info(f"Health: http://localhost:{port}/health")
    logger.info(f"Tools test: http://localhost:{port}/tools")


    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
    )

