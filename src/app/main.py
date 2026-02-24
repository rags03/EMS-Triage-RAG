from src.app.graph.edges import build_graph

def run_cli():
    graph = build_graph()
    config = {"configurable": {"thread_id": "1"}}

    print("Welcome to the OPQRST Pain Assessment Chatbot.")
    print("This tool provides general information only and is not medical advice.\n")

    state = {
        "onset": None, "provocation": None, "quality": None,
        "region": None, "severity": None, "time": None,
        "current_step": None, "current_question_text": None,
        "user_input": None, "complete": False, "summary": None
    }

    state = graph.invoke(state, config)
    print("Bot:", state.get("current_question_text"))

    while not state.get("summary"):
        user_input = input("You: ").strip()
        if not user_input:
            continue

        graph.update_state(config, {"user_input": user_input})
        state = graph.invoke(None, config)

        if state.get("current_question_text"):
            print("Bot:", state.get("current_question_text"))

    print("\n--- RECOMMENDATION ---")
    print(state.get("summary"))

if __name__ == "__main__":
    run_cli()