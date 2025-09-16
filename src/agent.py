from typing import TypedDict, Annotated, Sequence
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.messages.utils import count_tokens_approximately
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent
from langmem.short_term import SummarizationNode

load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    flag: str

def last_human_message(state: AgentState) -> HumanMessage:
    index = -1;
    while not isinstance(state["messages"][index], HumanMessage):
        index -= 1
    return state["messages"][index]

llm = init_chat_model("deepseek-chat", model_provider="deepseek")

"""
summarization_node = SummarizationNode(
    token_counter=count_tokens_approximately,
    model=llm,
    max_tokens=1024,
    max_summary_tokens=128,
    output_messages_key="llm_input_messages",
)

response_agent = create_react_agent(
    model=llm,
    tools=[],
    pre_model_hook=summarization_node,
    state_schema=AgentState,
    checkpointer=None,
)
"""