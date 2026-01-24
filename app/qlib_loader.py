import importlib
import os
import pkgutil
import sys


def load_all_modules(lib_folder_name="qlib"):
    lib_path = os.path.join(os.getcwd(), lib_folder_name)
    if not os.path.isdir(lib_path):
        raise FileNotFoundError(f"{lib_folder_name} folder not found at {lib_path}")

    parent_folder = os.path.abspath(os.path.join(lib_path, ".."))
    if parent_folder not in sys.path:
        sys.path.insert(0, parent_folder)

    package = importlib.import_module(lib_folder_name)

    for _, mod_name, is_pkg in pkgutil.iter_modules(package.__path__):
        full_name = f"{lib_folder_name}.{mod_name}"
        if full_name not in sys.modules:
            importlib.import_module(full_name)
