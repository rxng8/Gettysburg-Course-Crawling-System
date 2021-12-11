""" utils.py

"""

import requests
import json

def load_json_locators(path):
    data = None
    with open(path, "r") as f:
        data = json.loads(f.read())
    return data

def request_json_from_api(url: str):
    """[summary]

    Args:
        url (str): [description]

    Returns:
        [type]: [description]
    """
    res = requests.get(url)
    data = res.json()
    return data