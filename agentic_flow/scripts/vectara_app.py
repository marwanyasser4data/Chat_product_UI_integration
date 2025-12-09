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



'''
    Vectara Solution
'''

vectara_api = VectaraAPIs(api_key=os.getenv('VECTARA_API'))



def generate_response(message, session_key):
    print('entered the generation function')
    for i in vectara_api.interact_with_agent(agent_key='ASK_AML',
                              session_key=session_key,
                              message=message,
                              stream_response=True):
        # print(i.get('content', ''), end='', flush=True)
        yield i.get('content','')
