import json
from typing import Any


def read_text(path: str) -> str:
    with open(path, 'r') as f:
        data = f.read()
    return data


def read_json(path: str) -> Any:
    with open(path, 'r') as f:
        data = json.load(f)
    return data


def write_json(path: str, data: Any):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
