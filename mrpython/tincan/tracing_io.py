"""
Modify the file "backup_file" and keep a Json object with two keys:
"statements": a stack of statements that couldn't be sent (no internet, LRS malfunction...)
"""
from tincan import (tracing_config as config)
import json
import os

backup_filepath = config.backup_filepath
if not os.path.isfile(backup_filepath):
    with open(backup_filepath, "w") as f:
        data = {"statements": []}
        json.dump(data, f, indent=2)

def add_statement(statement):
    """Add a statement to the stack"""
    statement = statement.to_json()
    with open(backup_filepath, "r+") as f:
        data = json.load(f)
        list_statements = data["statements"]
        list_statements.append(statement)
        f.truncate(0)
        f.seek(0)
        json.dump(data, f, indent=2)


def get_statement():
    """Get the first statement of the stack"""
    with open(backup_filepath, "r") as f:
        data = json.load(f)
        list_statements = data["statements"]
        if list_statements:
            return list_statements[0]
    return None


def remove_statement():
    """Remove the first statement of the stack"""
    with open(backup_filepath, "r+") as f:
        data = json.load(f)
        if data["statements"]:
            data["statements"].pop(0)
        f.truncate(0)
        f.seek(0)
        json.dump(data, f, indent=2)
