from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from .nodes import ask_question, record_answer, generate_summary
from .state import PainAssessmentState

REQUIRED_FIELDS = ["onset", "provocation", "quality", "region", "severity", "time"]

def route_after_ask(state: PainAssessmentState) -> str:
    if state.get("complete"):
        return "summarize"
    return "record"

def build_graph():
    graph = StateGraph(PainAssessmentState)

    graph.add_node("ask", ask_question)
    graph.add_node("record", record_answer)
    graph.add_node("summarize", generate_summary)

    graph.add_edge(START, "ask")
    graph.add_conditional_edges("ask", route_after_ask, {"record": "record", "summarize": "summarize"})
    graph.add_edge("record", "ask")
    graph.add_edge("summarize", END)

    memory = MemorySaver()
    return graph.compile(checkpointer=memory, interrupt_before=["record"])