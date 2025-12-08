import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient  

mcp_configs = {'real_estate_sales': {'transport': 'streamable_http', 'url': 'https://semipolitical-kamari-unsymphoniously.ngrok-free.dev/mcp'}}

client = MultiServerMCPClient(mcp_configs)
 
async def async_fn(operation):
    return await operation
   
tools = asyncio.run(async_fn(client.get_tools()))

for t in tools:
    print(t.name)



print(asyncio.run(tools[0].ainvoke({'query': 'select * from apartments limit 1'})))