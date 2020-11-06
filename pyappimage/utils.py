
import os
import platform
import sys
import tempfile
import traceback

from .version import __version__
from pyappimage.constants import CATEGORIES, ENTRYPOINT


def replace_vars(string, vars):
    for var in vars:
        string = string.replace("${}".format(var), vars[var])
    return string


def verify_categories(data):
    for category in data.split(';'):
        if category not in CATEGORIES:
            print(category, "is not a valid 'category'")
            return False
    return True


def verify_bundle_id(data):
    if '.' in data:
        return True
    return False


def verify_entrypoint(_):
    return True


def get_input_else_default(default=None, _type=str, description="", verify=None):
    while True:
        try:
            data = _type(input(f"{description}: [{default}]: ").strip())
        except EOFError:
            continue
        except ValueError:
            print("Invalid data provided!")
            return None
        if not data or (isinstance(data, str) and data.isspace()):
            # we received something like empty space
            return default
        if verify is not None:
            if verify(data):
                return data
            else:
                print("Invalid data!")
                continue
        else:
            return data