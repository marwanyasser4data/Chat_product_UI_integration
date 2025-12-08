from langchain_core.language_models import FakeStreamingListLLM
from langgraph.checkpoint.memory import InMemorySaver  
from langchain.agents import create_agent
import time

llm = FakeStreamingListLLM(responses=['this is the first streaming output of a fake llm using a simple loop with a flush print'])
agent = create_agent(model=llm, checkpointer=InMemorySaver())

def generate_response(message, session_key):
    for events in agent.stream({'messages': message}, config={'configurable': {'thread_id': session_key}} , stream_mode='values'):
        msgs = events.get('messages')
        yield msgs[-1].content


# How to run (import from another script to integrate)
# for i in generate_response('hello', '1'):
#     print(i, end='', flush=True)