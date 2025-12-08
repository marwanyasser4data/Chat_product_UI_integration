from fastmcp import FastMCP
import asyncpg
from typing import Optional
import os
import sys

# Initialize FastMCP server
mcp = FastMCP("postgres-server")

# Database connection pool
pool: Optional[asyncpg.Pool] = None


async def get_pool() -> asyncpg.Pool:
    """Get or create database connection pool"""
    global pool
    if pool is None:
        pool = await asyncpg.create_pool(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", "5432")),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", ""),
            database=os.getenv("POSTGRES_DB", "postgres"),
            min_size=1,
            max_size=10,
        )
    return pool


@mcp.tool()
async def execute_query(query: str) -> str:
    """
    Execute a SQL query and return results.
    For SELECT queries, returns rows as JSON.
    For INSERT/UPDATE/DELETE, returns affected row count.
    
    Args:
        query: SQL query to execute
    """
    pool = await get_pool()
    
    try:
        async with pool.acquire() as conn:
            # Check if it's a SELECT query
            query_lower = query.strip().lower()
            if query_lower.startswith("select"):
                rows = await conn.fetch(query)
                if not rows:
                    return "No results found"
                
                # Convert to list of dicts
                results = [dict(row) for row in rows]
                return str(results)
            else:
                # For INSERT/UPDATE/DELETE/etc
                result = await conn.execute(query)
                return f"Query executed successfully: {result}"
                
    except Exception as e:
        return f"Error executing query: {str(e)}"


@mcp.tool(enabled=False)
async def list_tables(schema: str = "public") -> str:
    """
    List all tables in the specified schema.
    
    Args:
        schema: Database schema name (default: public)
    """
    pool = await get_pool()
    
    try:
        async with pool.acquire() as conn:
            query = """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = $1 AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """
            rows = await conn.fetch(query, schema)
            
            if not rows:
                return f"No tables found in schema '{schema}'"
            
            tables = [row["table_name"] for row in rows]
            return f"Tables in '{schema}': {', '.join(tables)}"
            
    except Exception as e:
        return f"Error listing tables: {str(e)}"


@mcp.tool(enabled=False)
async def describe_table(table_name: str, schema: str = "public") -> str:
    """
    Get the structure of a table including column names, types, and constraints.
    
    Args:
        table_name: Name of the table to describe
        schema: Database schema name (default: public)
    """
    pool = await get_pool()
    
    try:
        async with pool.acquire() as conn:
            query = """
                SELECT 
                    column_name,
                    data_type,
                    character_maximum_length,
                    is_nullable,
                    column_default
                FROM information_schema.columns
                WHERE table_schema = $1 AND table_name = $2
                ORDER BY ordinal_position
            """
            rows = await conn.fetch(query, schema, table_name)
            
            if not rows:
                return f"Table '{schema}.{table_name}' not found"
            
            result = f"Structure of table '{schema}.{table_name}':\n\n"
            for row in rows:
                col_type = row["data_type"]
                if row["character_maximum_length"]:
                    col_type += f"({row['character_maximum_length']})"
                
                nullable = "NULL" if row["is_nullable"] == "YES" else "NOT NULL"
                default = f" DEFAULT {row['column_default']}" if row["column_default"] else ""
                
                result += f"  {row['column_name']}: {col_type} {nullable}{default}\n"
            
            return result
            
    except Exception as e:
        return f"Error describing table: {str(e)}"

@mcp.tool()
async def get_distinct_values(
    table_name: str, 
    columns: str,
    schema: str = "public",
    limit: Optional[int] = None
) -> str:
    """
    Get distinct values for one or more columns in a table.
    
    Args:
        table_name: Name of the table
        columns: Comma-separated column names (e.g., "status" or "category,type")
        schema: Database schema name (default: public)
        limit: Optional limit on number of distinct rows returned
    """
    pool = await get_pool()
    
    try:
        async with pool.acquire() as conn:
            # Parse and clean column names
            column_list = [col.strip() for col in columns.split(",")]
            columns_str = ", ".join([f'"{col}"' for col in column_list])
            
            # Build query
            query = f'SELECT DISTINCT {columns_str} FROM "{schema}"."{table_name}" ORDER BY {columns_str}'
            
            if limit:
                query += f" LIMIT {limit}"
            
            rows = await conn.fetch(query)
            
            if not rows:
                return f"No distinct values found for {columns} in '{schema}.{table_name}'"
            
            # Convert to list of dicts
            results = [dict(row) for row in rows]
            
            result_str = f"Distinct values for {columns} in '{schema}.{table_name}' ({len(results)} rows"
            if limit:
                result_str += f", limited to {limit}"
            result_str += "):\n\n"
            result_str += str(results)
            
            return result_str
            
    except Exception as e:
        return f"Error getting distinct values: {str(e)}"
    
@mcp.tool(enabled=False)
async def list_schemas() -> str:
    """List all schemas in the database"""
    pool = await get_pool()
    
    try:
        async with pool.acquire() as conn:
            query = """
                SELECT schema_name 
                FROM information_schema.schemata
                WHERE schema_name NOT IN ('pg_catalog', 'information_schema')
                ORDER BY schema_name
            """
            rows = await conn.fetch(query)
            
            if not rows:
                return "No user schemas found"
            
            schemas = [row["schema_name"] for row in rows]
            return f"Schemas: {', '.join(schemas)}"
            
    except Exception as e:
        return f"Error listing schemas: {str(e)}"


@mcp.tool()
async def get_table_count(table_name: str, schema: str = "public") -> str:
    """
    Get the row count for a specific table.
    
    Args:
        table_name: Name of the table
        schema: Database schema name (default: public)
    """
    pool = await get_pool()
    
    try:
        async with pool.acquire() as conn:
            query = f'SELECT COUNT(*) as count FROM "{schema}"."{table_name}"'
            row = await conn.fetchrow(query)
            return f"Table '{schema}.{table_name}' has {row['count']} rows"
            
    except Exception as e:
        return f"Error getting table count: {str(e)}"


if __name__ == "__main__":
    # mcp.run()  # For stdio
    port = 3001

    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    mcp.run(
        transport="streamable-http", 
        host="0.0.0.0", 
        port=port
    )
