"""agent5/session_manager.py"""
from agent5.memory import ConversationMemory

# Simple in-memory session store: session_id -> ConversationMemory.
# No database, no Redis, per your architecture constraints.
# Sessions live only as long as the server process runs.
_SESSIONS = {}


def get_or_create_session(session_id: str) -> ConversationMemory:
    if session_id not in _SESSIONS:
        _SESSIONS[session_id] = ConversationMemory()
    return _SESSIONS[session_id]


def reset_session(session_id: str):
    if session_id in _SESSIONS:
        _SESSIONS[session_id].reset()


def delete_session(session_id: str):
    _SESSIONS.pop(session_id, None)