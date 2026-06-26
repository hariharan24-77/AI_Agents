import json
from datetime import datetime


def save_history(user_query, sql_query, result):
    history_entry = {
        "timestamp": datetime.now().strftime(
            "%d-%m-%Y %I:%M:%S %p"
        ),
        "user_query": user_query,
        "sql_query": sql_query,
        "result": str(result)
    }

    try:
        with open("chat_history.json", "r") as f:
            history = json.load(f)

    except (FileNotFoundError, json.JSONDecodeError):
        history = []

    history.append(history_entry)

    with open("chat_history.json", "w") as f:
        json.dump(history, f, indent=4)