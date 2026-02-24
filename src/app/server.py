import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from src.app.graph.edges import build_graph

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store graph sessions
sessions = {}

def get_session(session_id: str):
    if session_id not in sessions:
        graph = build_graph()
        config = {"configurable": {"thread_id": session_id}}
        initial_state = {
            "onset": None, "provocation": None, "quality": None,
            "region": None, "severity": None, "time": None,
            "current_step": None, "current_question_text": None,
            "user_input": None, "complete": False, "summary": None
        }
        state = graph.invoke(initial_state, config)
        sessions[session_id] = {"graph": graph, "config": config, "state": state}
    return sessions[session_id]

class UserInput(BaseModel):
    session_id: str
    message: str

@app.get("/start")
def start(session_id: str = "default"):
    session = get_session(session_id)
    return {"message": session["state"].get("current_question_text")}

@app.post("/chat")
def chat(body: UserInput):
    session = get_session(body.session_id)
    graph = session["graph"]
    config = session["config"]

    graph.update_state(config, {"user_input": body.message})
    state = graph.invoke(None, config)
    session["state"] = state

    if state.get("summary"):
        return {"message": state["summary"], "complete": True}
    return {"message": state.get("current_question_text"), "complete": False}

@app.get("/")
def root():
    return FileResponse("src/app/index.html")