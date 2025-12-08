from langchain_core.language_models import FakeStreamingListLLM
import time
from langchain_mcp_adapters.client import MultiServerMCPClient  
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent
import asyncio
import os
from pyngrok import ngrok
from scripts.tools import VectaraAPIs
from components.mcp_servers import get_localhost_real_estate_mcp
import json
print('vectara app module is imported !!!')


if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    # This runs ONLY once
    real_estate_mcp = get_localhost_real_estate_mcp()

    '''
        Configuring ngrok tunnel
    '''
    print('before start ngrok in my app')
    port = real_estate_mcp.port
    tunnel = ngrok.connect(port, 'http')
    print(f'ngrok tunnel url: {tunnel.public_url}')
    print('after strating ngrok in my app')

    print("Ngrok URL:", tunnel.public_url)
else:
    print("Skipping ngrok on auto-reloader process")


'''
    LangChain and OpenAI solution
# '''

# mcp_configs = {
#             real_estate_mcp.name: {
#                 "transport": real_estate_mcp.transport,  
#                 # "url": tunnel.public_url + '/mcp'
#                 'url': real_estate_mcp.url
#             }
#         }
# client = MultiServerMCPClient(mcp_configs)

# async def async_fn(operation):
#     return await operation
    
# tools = asyncio.run(async_fn(client.get_tools()))
# llm = ChatOpenAI(api_key=os.getenv('OPENROUTER_OPENAI_API_KEY'), 
#                  base_url=os.getenv('OPENROUTER_BASE_URL'), 
#                  model='openai/gpt-4.1-mini',
#                  max_tokens=2500,)
# agent = create_agent(model=llm, 
#                      tools=tools,
#                      system_prompt='''You are a real estate sales agent who help customers in KSA to get insights on appartments information
#                      Make sure to see columns names and unique values before running queries to get data.
#                      Data is in KSA and prices are in SAR
#                      ''')

# async def generate_response(human_message: str, config: dict):
#     async for msg, meta in agent.astream({'messages':[HumanMessage(human_message)]}, stream_mode='messages', config=config):
#         if meta.get('langgraph_node') == "model" and msg.id.startswith("lc_run"):
#             yield msg.content

# # Test function
# async def test():
#     async for i in generate_response('how many properties do we have?', config={'configurable': {'thread_id':'123'}}):
#         print(i,end='', flush=True)
# asyncio.run(test())


'''
    Vectara Solution
'''

vectara_api = VectaraAPIs(api_key=os.getenv('VECTARA_API'))



def generate_response(message, session_key):
    print('entered the generation function')
    for i in vectara_api.interact_with_agent(agent_key='real_estate_sales_ksa',
                              session_key=session_key,
                              message=message,
                              stream_response=True):
        # print(i.get('content', ''), end='', flush=True)
        yield i.get('content','')

# mcp_tools_config = {}
# tools = vectara_api.list_tools()
# values = json.loads(tools.text)
# for tool in values['tools']:
#     if tool['type'] =='mcp':
#         if tool.get('server_id', '') == 'tsr_35':
#             mcp_tools_config[tool['name']] = {'type': 'mcp', 'tool_id':tool['id']}

        

# # Create MCP server tool (and allow duplicate names)
# create_resposnse = vectara_api.create_tool_server(name='real_estate_ksa', 
#                                                   description='get the real estate data for KSA',
#                                                   mcp_url= tunnel.public_url + '/mcp',
#                                                   auth_token='abcdef......'
#                                                   )

# print(create_resposnse)
# print(create_resposnse.text)

# server_list = vectara_api.list_servers()
# print(server_list.text)



# create_agent_response = vectara_api.create_agent(key='real_estate_sales_ksa',
#                                                  name='real_estate_sales_ksa',
#                                                  department='real_estate',
#                                                  description='An agent that has the capability of giving insightfull numbers for buyers who want to buy appartments',
#                                                  tools_config=mcp_tools_config,
#                                                  system_prompt = '''You are a real estate sales agent who help customers in KSA to get insights on appartments information
#                                                  Make sure to see columns names and unique values before running queries to get data.
#                                                  Data is in KSA and prices are in SAR
#                                                  ''',
#                                                  model_name='gpt-4o-mini',
#                                                  enable_agent=True)
# print(type(create_agent_response))
# print(create_agent_response)
# print(create_agent_response.text)


# create_agent_session = vectara_api.create_agent_session(agent_key='real_estate_sales_ksa',
#                                                         session_key='real_estate_sales_ksa_session',
#                                                         name = 'first_real_estate_agent_session')

# print(create_agent_session)

# for i in vectara_api.interact_with_agent(agent_key='real_estate_sales_agent2',
#                               session_key='first_real_estate_agent_session',
#                               message='hala wala',
#                               stream_response=True):
#     print(i)
# print('done.')
# time.sleep(5000)