import streamlit as st
from src.app.graph.edges import build_graph

st.set_page_config(page_title="OPQRST Pain Assessment", page_icon="🏥")
st.title("🏥 OPQRST Pain Assessment Chatbot")
st.caption("This tool provides general information only and is not medical advice.")

# Initialize session state
if "graph" not in st.session_state:
    st.session_state.graph = build_graph()
    st.session_state.config = {"configurable": {"thread_id": "1"}}
    st.session_state.messages = []
    st.session_state.complete = False
    st.session_state.state = {
        "onset": None, "provocation": None, "quality": None,
        "region": None, "severity": None, "time": None,
        "current_step": None, "current_question_text": None,
        "user_input": None, "complete": False, "summary": None
    }
    # Run first invoke to get first question
    st.session_state.state = st.session_state.graph.invoke(
        st.session_state.state, st.session_state.config
    )
    first_question = st.session_state.state.get("current_question_text")
    st.session_state.messages.append({"role": "assistant", "content": first_question})

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Display summary if complete
if st.session_state.complete:
    st.success("Assessment complete!")
    st.stop()

# Chat input
if user_input := st.chat_input("Your answer..."):
    # Display user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Update graph state and invoke
    st.session_state.graph.update_state(st.session_state.config, {"user_input": user_input})
    st.session_state.state = st.session_state.graph.invoke(None, st.session_state.config)

    # Check for next question or summary
    if st.session_state.state.get("summary"):
        st.session_state.complete = True
        summary = st.session_state.state.get("summary")
        st.session_state.messages.append({"role": "assistant", "content": summary})
        with st.chat_message("assistant"):
            st.write(summary)
        st.success("Assessment complete!")
    elif st.session_state.state.get("current_question_text"):
        question = st.session_state.state.get("current_question_text")
        st.session_state.messages.append({"role": "assistant", "content": question})
        with st.chat_message("assistant"):
            st.write(question)

    st.rerun()