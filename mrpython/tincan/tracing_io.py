"""
Module that manage inputs/outputs in 3 files:

backup_filepath: Keep the statements that couldn't be sent after the statement was created.
We then try to send these statements during the execution of the app. (function clear_stack() of tracing_mrpython.py)

session_filepath: Keep the ID of the current session, the last active timestamp and if user allowed tracing.
If MrPython was closed and then re-opened in a 30 minutes window, the session ID is the same.
(function initialize_tracing() of tracing_mrpython.py)

debug_filepath: Keep all the statements in tracing_mrpython.py if debug_log is True
"""
from tincan import (tracing_config as config)
import json
import os
import threading
lock = threading.Lock()

backup_filepath = config.backup_filepath
session_filepath = config.session_filepath
debug_filepath = config.debug_filepath


# Backup file

def add_statement(statement):
    lock.acquire()
    """Add a statement to the stack"""

    statement = statement.to_json()
    with open(backup_filepath, "a+") as f:
        f.write(statement + '\n')
    lock.release()


def get_and_clear_stack():
    """Get the stack of statements and clear the stack"""
    if os.path.isfile(backup_filepath):
        with open(backup_filepath, "r+") as f:
            stack = f.readlines()
            f.truncate(0)
            return stack
    return None

# Session file


def session_file_exists():
    return os.path.isfile(session_filepath)


def get_session_info():
    with open(session_filepath, "r") as f:
        session_data = json.load(f)
    session = session_data["id-session"]
    active_time = session_data["active-timestamp"]
    tracing_enabled = session_data["tracing-enabled"]
    return session, active_time, tracing_enabled


def write_session_info(session, active_time, tracing_enabled):
    session_data = {"id-session": session, "active-timestamp": active_time, "tracing-enabled": tracing_enabled}
    with open(session_filepath, "w") as f:
        json.dump(session_data, f)


# Debug file

def initialize_debug_file():
    file = open(debug_filepath, "w")  # Write file and erase previous content
    file.close()
    print("Logging of created statements enabled for debug: All statements are kept in " + debug_filepath)


def add_statement_debug(statement, statement_number):
    if not os.path.isfile(debug_filepath):  # File creation
        initialize_debug_file()
    data = json.loads(statement.to_json())
    with open(debug_filepath, "a") as f:
        f.write("STATEMENT " + str(statement_number) + "\n")
        json.dump(data, f, indent=2)
        f.write("\n")
