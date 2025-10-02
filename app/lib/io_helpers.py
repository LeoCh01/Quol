import json
import logging
from typing import Any


def read_text(path: str) -> str:
    try:
        with open(path, 'r') as f:
            data = f.read()
        return data
    except Exception as e:
        logging.error(f'Failed to read text file {path} :: {e}', exc_info=True)
        return ''


def read_json(path: str) -> Any:
    try:
        with open(path, 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        logging.error(f'Failed to read JSON file {path} :: {e}', exc_info=True)
        return {}


def write_json(path: str, data: Any):
    try:
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logging.error(f'Failed to write JSON file {path} :: {e}', exc_info=True)
        pass
