from typing import TypedDict, Annotated, Sequence
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

llm = init_chat_model("deepseek-chat", model_provider="deepseek")

