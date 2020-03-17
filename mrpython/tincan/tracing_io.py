"""
Modify the file "tracing_data.json" and keep a Json object with two keys:
"student_hash": the hash used to identify a student
"statements": a stack of statements that couldn't be sent (no internet, LRS malfunction...)
"""
import json
import os

filename = os.path.join(os.path.dirname(__file__), 'tracing_data.json')
print(filename)


def reset_file():
    with open(filename, "w") as f:
        data = {"student_hash": "default", "list_statements" : []}
        json.dump(data, f)


def modify_student_hash(student_hash):
    with open(filename, "r+") as f:
        data = json.load(f)
        data["student_hash"] = student_hash
        f.truncate(0)
        f.seek(0)
        json.dump(data,f)


def get_student_hash():
    with open(filename, "r") as f:
        data = json.load(f)
        return(data["student_hash"])


def add_statement(statement):
    """Add a statement to the stack"""
    with open(filename, "r+") as f:
        data = json.load(f)
        list_statements = data["statements"]
        list_statements.append(statement)
        f.truncate(0)
        f.seek(0)
        json.dump(data,f)


def get_statement():
    """Get the first statement of the stack"""
    with open(filename, "r") as f:
        data = json.load(f)
        list_statements = data["statements"]
        if list_statements:
            return list_statements[0]


def remove_statement():
    """Remove the first statement of the stack"""
    with open(filename, "r+") as f:
        data = json.load(f)
        if data["statements"]:
            data["statements"].pop(0)
        f.truncate(0)
        f.seek(0)
        json.dump(data, f)

if __name__ == "__main__":
    print("io")
    """
    modify_student_hash("XXXXXX")
    print(get_student_hash())
    remove_statement()
    print(get_statement())
    """