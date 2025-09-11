from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.checkpoint.memory import InMemorySaver
from src.agent import AgentState, llm
import datetime

current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class Behavior(TypedDict):
    key: Annotated[
        str,
        """
        should be one of 'fetch', 'update' or 'chat'
        'fetch': 用户需要了解消费记录中的内容，应从数据库中检索条目
        'update': 用户的会话中含有提供的消费信息，应更新消费记录数据库
        'chat': 用户的话与消费无关，应进行简单的回复
        """
    ]

def choose_behavior(state: AgentState) -> str:
    """
    Decide whether to fetch data from database, update database or do simple chat.
    """
    structured_llm = llm.with_structured_output(Behavior)
    messages = [
        SystemMessage("根据以下用户消息，决定接下来的行为："),
        state["messages"][-1],
    ]
    behavior = structured_llm.invoke(messages)
    return behavior["key"]

def fetch_db_node(state: AgentState) -> AgentState:
    """
    Node to fetch data from the database.
    """
    # fetch data from the database
    fetched_record = db_manager.invoke(state["messages"][-1:] + [SystemMessage("根据以上消息从数据库中获取消费记录，返回检索到的记录的字符序列。")])
    return {"messages": [SystemMessage("SystemMessage: 用户可能希望了解的消费记录：" + str(fetched_record.content))]}

def update_db_node(state: AgentState) -> AgentState:
    """
    Node to update the database with new consumption information.
    """
    # update the database
    new_record = db_manager.invoke(state["messages"][-1:] + [SystemMessage("根据以上消息更新数据库中的消费记录，返回所更新的记录条目。")])
    return {"messages": [SystemMessage("SystemMessage: 消费记录已加入数据库：" + str(new_record))]}

def chat_node(state: AgentState) -> AgentState:
    """
    Node to handle simple chat.
    """
    response = llm.invoke(state["messages"])
    # response.pretty_print()
    return {"messages": [AIMessage(response.content)]}

def comment_node(state: AgentState) -> AgentState:
    """
    Node to comment on the consumption record.
    """
    prompt = "请对上一次SystemMessage中的消费记录进行简短的评论。"
    state["messages"].append(SystemMessage(prompt))
    response = llm.invoke(state["messages"])
    # response.pretty_print()
    return {"messages": [AIMessage(response.content)]}

graph = StateGraph(AgentState)
graph.add_node("fetch_db", fetch_db_node)
graph.add_node("update_db", update_db_node)
graph.add_node("chat", chat_node)
graph.add_node("comment", comment_node)
graph.add_conditional_edges(
    START,
    choose_behavior,
    {
        "fetch": "fetch_db",
        "update": "update_db",
        "chat": "chat"
    }
)
graph.add_edge("fetch_db", "comment")
graph.add_edge("update_db", "comment")
graph.add_edge("comment", END)
graph.add_edge("chat", END)

checkpointer = InMemorySaver()
app = graph.compile(checkpointer=checkpointer)
