# src/qabot/web/app.py
import uuid
import requests
import streamlit as st

from src.qabot.helpers.project_config import load_project_config
from src.qabot.api.schemas.schemas import Turn, AskRequest

project_config = load_project_config()

API_BASE = project_config['web']['frontend']['backend_host']
max_buffer = project_config['web']['frontend']['max_buffer']
hold_after_summarization = project_config['web']['frontend']['hold_after_summarization']

def init_state() -> None:
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "history_summary" not in st.session_state:
        st.session_state.history_summary = ""
    if "turns" not in st.session_state:
        st.session_state.turns = []   
    if "messages" not in st.session_state:
        st.session_state.messages = [] 


def summarize_if_needed(threshold: int = 6) -> None:
    if len(st.session_state.turns) <= threshold:
        return
    try:
        response = requests.post(
            f"{API_BASE}/summarize",
            json={
                "session_id": st.session_state.session_id,
                "last_turns": st.session_state.turns,
                "history_summary": st.session_state.history_summary,
            },
            timeout=30,
        )
        response.raise_for_status()
        st.session_state.history_summary = response.json()["history_summary"]
        st.session_state.turns = st.session_state.turns[-hold_after_summarization:]
    except requests.RequestException as exc:
        st.warning(f"Update unsuccessful: {exc}")

def send_message(question: str) -> None:
    """
    Sends question to ask/ endpoint and save it along with answer to appropriate session_state fields
    """
    
    summarize_if_needed(threshold=max_buffer)
    payload = AskRequest(
        session_id = st.session_state.session_id,
        history_summary = st.session_state.history_summary,
        last_turns = st.session_state.turns,
        question = question,
    ).model_dump()
    st.session_state.turns.append({"role": "user", "content": question})
    try:
        response = requests.post(f"{API_BASE}/ask", json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        st.session_state.messages.append(("assistant", f"⚠️ {exc}", []))
        return

    answer = data["answer"]
    sources = data.get("sources", [])
    st.session_state.turns.append({"role": "assistant", "content": answer})
    st.session_state.messages.append(("assistant", answer, sources))

    

def main() -> None:
    st.set_page_config(page_title="🌊RAG Chat🌊", page_icon="🔥", layout="wide")
    init_state()

    st.title("Welcome to techincal support assistant🍀\n Have any issues?")

    col_left, col_right = st.columns([3, 1])
    with col_right:
        if st.button("Reset chat"):
            for key in ("session_id", "history_summary", "turns", "messages"):
                st.session_state.pop(key, None)
            init_state()
            

    with col_left:
        for role, content, sources in st.session_state.messages:
            bubble = st.chat_message(role)
            bubble.write(content)
            if sources and role == "assistant":
                sources_html = "<details><summary>Retrieved Sources</summary><ul>"
                for idx, src in enumerate(sources, start=1):
                    sources_html += f"<li>{idx}. <b>{src['title']}</b> : <code>{src['path']}</code> (Updated: {src['updated_at']})</li>"
                sources_html += "</ul></details>"
                bubble.markdown(sources_html, unsafe_allow_html=True)
                

        user_prompt = st.chat_input("Ask a question…")
        if user_prompt:
            st.session_state.messages.append(("user", user_prompt, []))
            send_message(user_prompt)
            st.rerun()
    

if __name__ == "__main__":
    main()
