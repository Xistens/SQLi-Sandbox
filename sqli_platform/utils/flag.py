#!/usr/bin/python3
import fileinput
from sqli_platform import app, _configs


def get_flag(challenge: str):
    """
    Retrieves the flag from the _configs object

    Args:
        challenge:  (str) The name of the challenge to retrieve the flag from
    Return:
        Returns the flag (str) if it is found, else it will return None
    """
    for conf in _configs:
        name = conf["config"]["name"]
        if name == challenge:
            return conf["config"].get("flag", None)
    return None


def place_flag_schema(schema: str, challenge: str):
    """
    Helper function to place flag from config into the database schema.
    It looks for {{FLAG}} inside the schema file and replaces it with the flag.

    Args:
        schema:     (str) Path to the schema where the flag will be placed
        challenge:  (str) The challenge name to get the flag from
    """
    try:
        with open(schema, "r+") as f:
            data = f.read()
            if "{{FLAG}}" in data:
                flag = get_flag(challenge)
                new_data = data.replace("{{FLAG}}", flag)
                f.write(new_data)
    except IOError:
        raise IOError(f"Error placing flag in {schema} for challenge {challenge}")
