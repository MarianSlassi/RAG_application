# src/qabot/web/app.py
import uuid
import requests
import streamlit as st

API_BASE = "http://127.0.0.1:8000"

def init_state() -> None:
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "history_summary" not in st.session_state:
        st.session_state.history_summary = ""
    if "turns" not in st.session_state:
        st.session_state.turns = []   # list[dict(role, content)]
    if "messages" not in st.session_state:
        st.session_state.messages = []  # list[(role, content, sources)]

def last_turns(payload_turns: list[dict], window: int = 4) -> list[dict]:
    return payload_turns[-window:]

def summarize_if_needed(threshold: int = 6) -> None:
    if len(st.session_state.turns) < threshold:
        return
    try:
        response = requests.post(
            f"{API_BASE}/summarize",
            json={
                "session_id": st.session_state.session_id,
                "turns": st.session_state.turns,
                "current_summary": st.session_state.history_summary,
            },
            timeout=30,
        )
        response.raise_for_status()
        st.session_state.history_summary = response.json()["summary"]
        st.session_state.turns = st.session_state.turns[-4:]
    except requests.RequestException as exc:
        st.warning(f"Update unsuccessful: {exc}")

def send_message(question: str, show_sources: bool) -> None:
    payload = {
        "session_id": st.session_state.session_id,
        "history_summary": st.session_state.history_summary,
        "last_turns": last_turns(st.session_state.turns),
        "question": question,
    }
    st.session_state.turns.append({"role": "user", "content": question})
    try:
        response = requests.post(f"{API_BASE}/ask", json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        st.session_state.messages.append(("assistant", f"⚠️ {exc}", []))
        return

    st.session_state.turns.append({"role": "assistant", "content": data["answer"]})
    st.session_state.messages.append(
        ("assistant", data["answer"], data.get("sources", []) if show_sources else [])
    )
    summarize_if_needed()

def main() -> None:
    st.set_page_config(page_title="RAG Chat", page_icon="💬", layout="wide")
    init_state()

    st.title("RAG Chat")

    col_left, col_right = st.columns([3, 1])
    with col_right:
        show_sources = st.checkbox("Show Sources")
        if st.button("Reset chat"):
            for key in ("session_id", "history_summary", "turns", "messages"):
                st.session_state.pop(key, None)
            init_state()
            

    with col_left:
        for role, content, sources in st.session_state.messages:
            bubble = st.chat_message(role)
            bubble.write(content)
            if sources:
                with bubble.expander("Sources"):
                    for idx, src in enumerate(sources, start=1):
                        bubble.markdown(
                            f"{idx}. **{src['title']}** – `{src['path']}` (Updated: {src['updated_at']})"
                        )

        user_prompt = st.chat_input("Ask a question…")
        if user_prompt:
            st.session_state.messages.append(("user", user_prompt, []))
            send_message(user_prompt, show_sources)
            

if __name__ == "__main__":
    main()
