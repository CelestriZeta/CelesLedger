from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.checkpoint.memory import InMemorySaver
import datetime
from src.agent import AgentState, llm
from src.database import db, Record, db_creation_script

current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

checkpointer = InMemorySaver()
"""
store = InMemoryStore(
    index={
        "embed": init_embeddings("openai:text-embedding-3-small"),  # Embedding provider
        "dims": 1536,                              # Embedding dimensions
        "fields": ["message"]              # Fields to embed
    }
)
"""

class Behavior(TypedDict):
    key: Annotated[
        str,
        """
        只能为'fetch','update'和'chat'之一;
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
    query = llm.invoke([SystemMessage(
f"""
你是一个专业的SQL查询生成器。你的任务是在记录消费的表中，按照用户提供的自然语言描述: {state["messages"][-1]}生成标准且可执行的SQL查询语句，获取一整行的信息。

数据库表的结构如下：{db_creation_script}
## 数据库表各列描述：
1. id: primary key
2. item: 所购物品的名称
3. cost: 此次消费或进账的金额，消费记录为负值，进账为正值
4. time: 此次消费或进账发生的时间，以"YYYY-MM-DD"格式记载。当前的时间为{current_time}，请结合用户输入确定消费或进账发生的时间
5. type: 此条记录所属的类型，按照居民消费八大类分类，只能为以下几种：
- 食品烟酒
- 衣着
- 居住
- 生活用品及服务
- 交通通信
- 教育文化娱乐
- 医疗保健
- 其它用品及服务
6. subtype: 此条记录所属的，type所填分类下的子类型
7. original_message: 此条记录对应的用户消息原文

注意事项：
- SQL语句不可修改数据库
- 只返回SQL查询语句，不要包含任何解释或额外信息
- 输出中不要包含任何XML标签
- 输出中不要包含任何Markdown语法
- 确保SQL语法标准且可在SQLite中执行
"""
    ),])
    print(query.content)
    try:
        fetched_record = db.execute(query.content)
    except Exception as e:
        print(f"执行SQL查询时出错: {e}")
    return {"messages": [SystemMessage("SystemMessage: 用户可能希望了解的消费记录：" + str(fetched_record))]}

def update_db_node(state: AgentState) -> AgentState:
    """
    Node to update the database with new consumption information.
    """
    # update the database
    structured_llm = llm.with_structured_output(Record)
    record = structured_llm.invoke([SystemMessage(
    f"""
    你是一个专业的消费记录信息提取器。你的任务是按照用户提供的自然语言描述: {state["messages"][-1]}, 总结出此条消费记录各个参数的值。
    其中，当前的时间为{current_time}。
    """
    ),])
    record["original_message"] = state["messages"][-1].content
    for k in ["item", "cost", "time", "type", "subtype", "original_message"]:
        if k not in record:
            record[k] = None
    db.add_record(record)
    return {"messages": [SystemMessage("SystemMessage: 消费记录已加入数据库：" + str(record))]}

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
    prompt = "请对上一次查询到的或记录的消费记录进行简短的评论。"
    response = llm.invoke(state["messages"] + [SystemMessage(prompt)])
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

app = graph.compile(
    checkpointer=checkpointer,
)
