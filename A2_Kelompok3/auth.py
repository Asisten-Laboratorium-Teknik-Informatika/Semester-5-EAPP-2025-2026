# auth.py
import eel
from db import register_user_in_db, login_user_in_db

active_sessions = {}

@eel.expose
def register_user(session_id, username, email, password):
    success, message = register_user_in_db(username, email, password)
    if not success:
        return {"success": False, "message": message}

    user_data = {"username": username, "email": email}
    active_sessions[session_id] = user_data
    return {"success": True, "message": message, "user": user_data}


@eel.expose
def login_user(session_id, email, password):
    success, user_data, message = login_user_in_db(email, password)
    if not success:
        return {"success": False, "message": message}

    active_sessions[session_id] = user_data
    return {"success": True, "message": message, "user": user_data}


@eel.expose
def get_current_user(session_id):
    return active_sessions.get(session_id)


@eel.expose
def logout(session_id):
    if session_id in active_sessions:
        del active_sessions[session_id]
