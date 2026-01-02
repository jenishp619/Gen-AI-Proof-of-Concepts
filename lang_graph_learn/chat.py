from dotenv import load_dotenv
from typing_extensions import TypedDict,Annotated
from langchain.messages import AnyMessage
from langgraph.graph.message import add_messages
import operator
from langgraph.graph import StateGraph, START,END
from langchain.chat_models import init_chat_model
load_dotenv()
llm = init_chat_model(
     model="gpt-4.1-mini",
     model_provider="openai"
)
class State(TypedDict):
     messages: Annotated[list[AnyMessage], add_messages]

# Node creation / Function
def chatbot(state:State):
     response = llm.invoke(state.get("messages"))
     print("\n\nInside chatbot node",state)
     return {"messages":response}

def samplenode(state:State):
     print("\n\nInside sample node",state)
     return {"messages":["Sample message appended"]}
     


# Providing the current strucutre(model) of State to stategraph
graph_builder = StateGraph(State)
# adding nodes
graph_builder.add_node("chatbot",chatbot)
graph_builder.add_node("samplenode",samplenode)
# Adding edges (workflow)
graph_builder.add_edge(START,"chatbot")
graph_builder.add_edge("chatbot","samplenode")
graph_builder.add_edge("samplenode",END)

graph = graph_builder.compile()

updated_state = graph.invoke(State({"messages":["Hi, My name is Jenish Patel"]}))

print("\n\nupdated state",updated_state)
# START -> chatbot -> samplenode -> END