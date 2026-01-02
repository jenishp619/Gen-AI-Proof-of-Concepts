from dotenv import load_dotenv
from typing_extensions import TypedDict
from typing import Optional, Literal
from langgraph.graph import StateGraph, START,END
from openai import OpenAI

load_dotenv()
client = OpenAI()

class State(TypedDict):
    user_query: str
    llm_output : Optional[str]
    is_good : Optional[bool]

def chatbot(state:State):
    print("Chatbot node",state)
    response =  client.chat.completions.create(
        model="gpt-4.1-mini",
        messages = [
            {"role":"user","content":state.get("user_query")}
        ]
    )
    state["llm_output"] = response.choices[0].message.content
    return state

def evaluate_response(state:State) -> Literal["chatbot_gemini","endnode"]:
    print("Evaluate node",state)
    response = state.get("llm_output", "")
    
    # Create an evaluation prompt for GPT to assess the response quality
    evaluation_prompt = f"""Evaluate if this response is complete and accurate. Check for:
    1. Response: {response}
    2. Original question: {state.get('user_query')}
    
    Evaluate based on:
    - Relevance to the question
    - Completeness of answer
    - Accuracy of information
    - Clarity of explanation
    
    Respond with only 'good' or 'bad'."""
    
    eval_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": evaluation_prompt}]
    )
    
    evaluation = eval_response.choices[0].message.content.strip().lower()
    
    # If evaluation says 'good', end the conversation
    if evaluation == 'good':
        return "endnode"
    
    # If evaluation says 'bad', try with Gemini
    return "chatbot_gemini"
def chatbot_gemini(state:State):
    print("Gemini node",state)
    response =  client.chat.completions.create(
        model="gpt-4.1-mini",
        messages = [
            {"role":"user","content":state.get("user_query")}
        ]
    )
    state["llm_output"] = response.choices[0].message.content
    return state
def endnode(state:State):
    return state
graph_builder = StateGraph(State)

graph_builder.add_node("chatbot",chatbot)
graph_builder.add_node("chatbot_gemini",chatbot_gemini)
graph_builder.add_node("endnode",endnode)

graph_builder.add_edge(START,"chatbot")
graph_builder.add_conditional_edges("chatbot",evaluate_response)
graph_builder.add_edge("chatbot_gemini","endnode")
graph_builder.add_edge("endnode",END)

graph = graph_builder.compile()

updated_state = graph.invoke(State({"user_query":"Hey what is 2+2? "}))
print("updated-state",updated_state)