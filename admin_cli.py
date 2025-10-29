import sys
import yaml
import uuid
from pathlib import Path

API_KEYS_PATH = Path("config/api_keys.yaml")

def load_keys():
    if API_KEYS_PATH.exists():
        with open(API_KEYS_PATH) as f:
            return yaml.safe_load(f)
    return {}

def save_keys(keys):
    with open(API_KEYS_PATH, "w") as f:
        yaml.safe_dump(keys, f)

def add_key(username):
    keys = load_keys()
    if username in keys:
        print("User already exists.")
        return
    keys[username] = str(uuid.uuid4())
    save_keys(keys)
    print(f"Key for {username}: {keys[username]}")

def list_keys():
    keys = load_keys()
    for user, key in keys.items():
        print(f"{user}: {key}")

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "add":
        add_key(sys.argv[2])
    elif cmd == "list":
        list_keys()
    else:
        print("Usage: python admin_cli.py [add <user> | list]")
