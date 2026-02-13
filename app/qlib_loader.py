import importlib
import os
import pkgutil
import sys

from globals import BASE_DIR


def load_all_modules(lib_folder_name: str = "qlib") -> None:
    lib_path = os.path.join(BASE_DIR, lib_folder_name)

    if not os.path.isdir(lib_path):
        raise FileNotFoundError(f"{lib_folder_name} folder not found at {lib_path}")

    if BASE_DIR not in sys.path:
        sys.path.insert(0, BASE_DIR)

    package = importlib.import_module(lib_folder_name)

    for _, mod_name, _ in pkgutil.iter_modules(package.__path__):
        full_name = f"{lib_folder_name}.{mod_name}"
        if full_name not in sys.modules:
            importlib.import_module(full_name)
