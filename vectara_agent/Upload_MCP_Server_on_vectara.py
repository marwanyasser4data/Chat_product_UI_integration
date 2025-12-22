

import http.client
import json

conn = http.client.HTTPSConnection("api.vectara.io")

payload = {
  "name": "AML_MCP",
  "type": "mcp",
  "description": "AML postgres mcp",
  "uri": "https://nonabusively-oxlike-roy.ngrok-free.dev/mcp",
  "headers": {},
  "transport": "streamable-http",  # or "sse" if that matches your server
  "enabled": True,
  "metadata": {}
}

headers = {
  "Content-Type": "application/json",
  "Accept": "application/json",
  "x-api-key": 'zut_6l8-IbJFbTupoqfyb28_c0m0VRm4JV5_xnw8ZQ'
}

conn.request("POST", "/v2/tool_servers", json.dumps(payload), headers)
res = conn.getresponse()
data = res.read()

print("Status:", res.status, res.reason)
print("Body:", data.decode("utf-8"))

