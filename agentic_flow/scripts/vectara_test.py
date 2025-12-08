import requests
import json
import asyncio
from scripts.tools import VectaraAPIs
import os
import arabic_reshaper
from dotenv import load_dotenv
load_dotenv()

vectara_api = VectaraAPIs(api_key=os.getenv('VECTARA_API'))

for i in vectara_api.interact_with_agent(agent_key='real_estate_sales_ksa',
                              session_key='first_real_estate_agent_session_test',
                              message='Hi',
                              stream_response=True):
    content = i.get('content', '')
    if isinstance(content, bytes):
        content = content.decode('utf-8')
    print(content, end='', flush=True)
# print(arabic_reshaper.reshape('اهلا'))