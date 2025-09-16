from src.graph import run_postgres_graph, run_inmemory_graph

def main():
    config = {"configurable": {"thread_id": "1", "user_id": "1"}}

    # user_input = input("Input: ")
    user_input = "我昨天花了300块买了个音箱"

    # run_postgres_graph(user_input, config)
    run_inmemory_graph(user_input, config)


if __name__ == "__main__":
    # db.clear()
    main()

