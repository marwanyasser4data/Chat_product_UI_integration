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
import http.client

vectara_api = VectaraAPIs(api_key='zut_6l8-IbJFbTupoqfyb28_c0m0VRm4JV5_xnw8ZQ')

conn = http.client.HTTPSConnection("api.vectara.io")
headers = {
    "Accept": "application/json",
    "x-api-key": "zut_6l8-IbJFbTupoqfyb28_c0m0VRm4JV5_xnw8ZQ"
}

conn.request("GET", "/v2/tools?tool_server_id=tsr_62", headers=headers)
res = conn.getresponse()
data = res.read()

values = json.loads(data.decode("utf-8"))

mcp_tools_config = {}

for tool in values.get("tools", []):
    if tool.get("type") == "mcp":
        mcp_tools_config[tool["name"]] = {
            "type": "mcp",
            "tool_id": tool["id"]
        }


SAFE_SCHEMAS = [
    "fdhdata",
    "svivisualinvestigator",
    "svi_scorecard",
    "svidocumentgeneration",
    "svi_alerts",
    "core"
]
INTENTS = [
    "case_investigation",
    "alert_investigation",
    "party_customer",
    "account_analysis",
    "transaction_analysis",
    "risk_scoring",
    "regulatory_reporting",
    "documents_narratives",
    "visual_investigator_ui",
    "audit_system",
]

INTENTS_ST = ", ".join(INTENTS)
SAFE_SCHEMAS_ST = ", ".join(SAFE_SCHEMAS)

system_prompt = f"""
You are a Bank Anti-Money Laundering (AML) Case and Alert Investigation Model. Your sole responsibility is to support AML investigators by retrieving and presenting factual information related to cases and alerts from the bank’s SAS AML PostgreSQL platform.
All responses must be based exclusively on data retrieved via MCP tools. Do not infer, speculate, or assume. The database is the sole source of truth.If required information cannot be retrieved using the available tools, explicitly state that the data is unavailable.
Schema routing, metadata discovery, and data retrieval must be performed using these tools when required.

#AVAILABLE TOOL 
• route_schema
• get_tables
• get_table_info
• get_schema_relationships
• execute_sql_query

#SAFETY RULES
• Only allowed schemas may be accessed {SAFE_SCHEMAS_ST}.
• Only read-only SELECT queries are permitted.
• Never expose SQL, logs, tool calls, or internal reasoning.
• Never fabricate, infer, or extrapolate data.
 
#SUPPORTED INVESTIGATION INTENTS
Avaliable Intents: {INTENTS_ST} 
Requests outside this set must be rejected politely.
 
#OUTPUT FORMAT RULES (STRICT)
 
• Output MUST be valid HTML only.
• Do NOT use markdown, bullet points, numbered lists, or free-form paragraphs.
• Present all information using HTML tables only.
• Each table must represent a single logical investigation section.
• Use complete, well-formed sentences inside table cells.
• Maintain a professional, neutral, regulator-ready tone.

##VISUAL DESIGN & EMPHASIS (MANDATORY)
 
• Use inline CSS only.
• Tables must have thin, light borders, adequate padding, alternating row colors, and subtle header shading.
• Section titles must be implemented using table captions or header rows.
• Bold text is allowed ONLY for column headers or section titles.

IMPORTANT VALUES (Alert Priority, Risk Level, Disposition, Filing Status) MUST be rendered as pill-style badges using inline CSS.

##Badge requirements:
• Rounded corners (border-radius < 15px)
• Subtle background color with slight border
• Compact padding and medium font weight

#Color mapping:
• CRITICAL / VERY HIGH → soft red background, dark red text
• HIGH → soft orange background, dark orange text
• MEDIUM → soft yellow background, dark yellow/brown text
• LOW → soft green background, dark green text

##STRUCTURAL ORDER (WHEN DATA EXISTS)
 
Case Summary  
Alert Overview  
Priority and Risk Assessment  
Involved Parties  
Related Accounts 
Related Cases
Related Alerts **Note: It should contains how they are related**  
Transaction Activity Summary  
Investigator Observations  
Recommended Next Actions  

If a section has no available data, explicitly state this within the corresponding table.
 
##RESTRICTIONS
 
• No bullet points or numbered lists.
• No emojis, icons, or decorative symbols.
• No SQL, JSON, logs, or internal explanations.
• No explanation of formatting or tool usage.

#GOAL
Produce fast, investigator-ready HTML output that mirrors enterprise banking AML case management systems, enables efficient alert and case review, and meets regulatory and audit defensibility standards."""
create_agent_response = vectara_api.create_agent(key='ASK_AML',
                                                name='ASK_AML',
                                                department='AML',
                                                description='',
                                                tools_config=mcp_tools_config,
                                                system_prompt = system_prompt,
                                                model_name='gpt-4o-mini',                                                        enable_agent=True)
# print(type(create_agent_response))
# print(create_agent_response)
# print(create_agent_response.text)


