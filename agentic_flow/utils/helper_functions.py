from PIL import Image
import io
from langchain_core.messages import AnyMessage, HumanMessage

def graph_as_pil_image(graph):
    img = Image.open(io.BytesIO(graph.get_graph(xray=True).draw_mermaid_png()))
    return img


def format_chat_history(chat_list: list[AnyMessage]):
    final = []
    for message in chat_list:
        if isinstance(message, HumanMessage):
            final.append(('User', message.content))
        else:
            final.append(('Assistant', message.content))
    return final