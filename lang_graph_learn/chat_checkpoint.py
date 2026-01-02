from dotenv import load_dotenv
from typing_extensions import TypedDict,Annotated
from langchain.messages import AnyMessage
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START,END
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.mongodb import MongoDBSaver
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

     

# Providing the current strucutre(model) of State to stategraph
graph_builder = StateGraph(State)
# adding nodes
graph_builder.add_node("chatbot",chatbot)
# Adding edges (workflow)
graph_builder.add_edge(START,"chatbot")
graph_builder.add_edge("chatbot",END)


graph = graph_builder.compile()

def compile_graph_with_checkpointer(checkpointer):   
     return graph_builder.compile(checkpointer=checkpointer)
DB_URI = "mongodb://admin:admin@localhost:27017"
with MongoDBSaver.from_conn_string(DB_URI) as checkpointer:    
     graph_with_checkpointer = compile_graph_with_checkpointer(checkpointer=checkpointer)

     config = {
          "configurable":{
               "thread_id":"jenish"
          }
               }
     # config = {
     #      "configurable":{
               # "thread_id":"aman"  (user_id)
     #      }
     #           }
     # Two threads means you can store different sessions in the db one thread/user
     
     for chunk in graph_with_checkpointer.stream(
        {"messages": [{"role": "user", "content": "am i learning good field? "}]},
        config,  
        stream_mode="values"
                              ):
        chunk["messages"][-1].pretty_print()
     # updated_state = graph_with_checkpointer.invoke(State({"messages":["what is my name?"]}),
     #                                           config)

     # print("\n\nupdated state",updated_state)
# START -> chatbot -> END
# Checkpointer (jenish)- Hey my name is Jenish P