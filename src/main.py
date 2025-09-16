from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, SystemMessage, ToolMessage

from src.graph import app
from src.database import db

def print_stream(stream):
    for event in stream:
        event["messages"][-1].pretty_print()

def main():
    config = {"configurable": {"thread_id": "1", "user_id": "1"}}

    # user_input = input("Input: ")
    user_input = "我午饭花了多少钱？"

    while user_input.lower() not in ["exit", "quit"]:
        print_stream(app.stream(
            {"messages": [HumanMessage(user_input)]},
            config=config,
            stream_mode="values"
        ))
        user_input = input("Input: ")

    print("Exiting...")
    db.close()

if __name__ == "__main__":
    # db.clear()
    main()

