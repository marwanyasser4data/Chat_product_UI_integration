import http.client
import json

conn = http.client.HTTPSConnection("api.vectara.io")
payload = json.dumps({
  "key": "customers_sql_agent",
  "name": "Customer SQL Agent",
  "description": "Converts natural language to SQL for the customers table",
  "model": {
    "name": "gpt-4o-mini",
    "parameters": {
      "temperature": 0,
      "max_tokens": 500
    }
  },
  "first_step": {
    "type": "conversational",
    "instructions": [
      {
        "type": "initial",
        "name": "SQL Instruction",
        "description": "Generates SQL using fixed table schema",
        "template_type": "velocity",
        "template": """
You are a Text-to-SQL expert. Convert the natural language question into valid SQL.
The SQL must query a table called real_estate.

RULES:
- Return ONLY SQL.
- Do NOT add explanations or comments.
- Return ONLY raw SQL.
- Do NOT wrap the answer in ```sql or any code block.
- Do NOT add backticks.
- Do NOT format in markdown.
- Only return the SQL query.
                    """,
        "enabled": True
      }
    ],
    "output_parser": {
      "type": "default"
    }
  },
  "enabled": True
})
headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  'x-api-key': 'zut_OCWxW4qNbpS8eVNM4-mbTuRcPDDVT8my8zrgVA'
}
conn.request("POST", "/v2/agents", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))