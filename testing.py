from agentic_flow.scripts.vectara_app import generate_response


for i in generate_response('hello man', '123'):
    print(i, end='', flush=True)
