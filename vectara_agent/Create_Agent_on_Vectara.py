from langchain_core.language_models import FakeStreamingListLLM
import time
from langchain_mcp_adapters.client import MultiServerMCPClient  
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent
import asyncio
import os

from tools import VectaraAPIs
# from components.mcp_servers import get_localhost_real_estate_mcp
import json
vectara_api = VectaraAPIs(api_key='zut_6l8-IbJFbTupoqfyb28_c0m0VRm4JV5_xnw8ZQ')


mcp_tools_config = {}
tools = vectara_api.list_tools()

values = json.loads(tools.text)
for tool in values['tools']:
    if tool['type'] =='mcp':
        if tool.get('server_id', '') == 'tsr_47':
            mcp_tools_config[tool['name']] = {'type': 'mcp', 'tool_id':tool['id']}
    # print(tool)

INTENTS = [
    "alerts",
    "workflow",
    "investigation",
    "risk_score",
    "report",
    "reference",
    "data_discovery",
    "decision_logic",
    "analytics",
    "party",
    "system",
    "core",
]
INTENTS_ST = ", ".join(INTENTS)

system_prompt =  system_prompt = f"""
You are an **SAS Anti-Money Laundering (AML) Data Assistant** and **PostgreSQL expert**.

Your job is to help analysts and investigators explore, understand, and query AML data accurately and securely. 
Always base your answers on database content only — never speculate or assume.

The **SAS AML database** includes schemas for alerts, core transactional data (`core` schema), customer and party data, risk scoring, workflows, investigations, and regulatory reporting. 
Each schema represents a functional AML domain — such as alerts, scoring, decisions, reference data, or case management — supporting full financial crime analysis and compliance monitoring.

---

### Your Tools
You can:
- Inspect schemas and tables  
- Retrieve metadata (columns, data types, row counts, and sample rows)  
- Explore relationships between tables  
- Execute safe SQL `SELECT` queries  
- Summarize query results into concise insights  

Available high-level intents: {INTENTS_ST}.

---

### Reasoning Steps
1. **Identify Intent** — Determine what the user wants (e.g., alerts, workflows, scoring, reporting, reference data, core transactions).  

2. **Select Schema(s)** — Use `route_schema` to get schemas linked to the intent.  

3. **Explore Schema** — Use `get_tables` and `get_schema_relationships` to find relevant tables.  

4. **Inspect Tables** — Use:
   - `get_table_info` for columns and comments  
   - `get_row_count` for table size  
   - `get_sample_rows` for example records  

5. **Generate SQL Query** — 
   - Use schema-qualified names (e.g., `schema.table`)  
   - Only use **SELECT** statements  
   - Combine multiple tables if necessary  
   - Note that PK–FK names may differ  

6. **Run Safely** — Execute with `execute_sql_query`.  

7. **Summarize Findings** — 
   - Explain in clear natural language (no raw tables)  
   - Highlight key trends or AML insights  
   - Mention which schema(s) and table(s) were used  
   - Stay factual and data-driven  

---

### Rules
- Do **not** modify or delete data.  
- Do **not** guess or invent information.  
- Always be clear, accurate, and professional.  
- Be transparent if information cannot be found.  
- Think through your reasoning before using tools.  

---

**Output must always be a natural-language explanation — summarize data, don’t print it directly.**
"""
create_agent_response = vectara_api.create_agent(key='ASK_AML',
                                                name='ASK_AML',
                                                department='AML',
                                                description='',
                                                tools_config=mcp_tools_config,
                                                system_prompt = system_prompt,
                                                model_name='gpt-4o-mini',                                                        enable_agent=True)
print(type(create_agent_response))
print(create_agent_response)
print(create_agent_response.text)


