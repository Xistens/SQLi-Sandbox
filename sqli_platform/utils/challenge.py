#!/usr/bin/python3
import fileinput
from sqli_platform import app, _configs

def get_config(challenge: str, key: str):
    """
    Retrieves the flag from the _configs object

    Args:
        challenge:  (str) The name of the challenge to retrieve the flag from
        key:       (str) The name of the configuration to retrieve
    Return:
        Returns the value of the configuration if it is found, else it will return none.
    """
    for conf in _configs:
        name = conf["config"]["name"]
        if name == challenge:
            return conf["config"].get(key, None)
    return None

def get_flag(challenge: str):
    """
    Retrieves the flag from the _configs object. Abstraction...

    Args:
        challenge:  (str) The name of the challenge to retrieve the flag from
    Return:
        Returns the flag (str) if it is found, else it will return None
    """
    return get_config(challenge, "flag")


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


def format_query(queries: list = []) -> str:
    """
    Helper function to format the database query to display for the user

    Args:
        queries:      (list) A list containing queries or a list containing
                        tuples with queries and input parameters.
    Return:
        string:       (str) The formatted output
    """
    string = ""
    for item in queries:
        if type(item) is tuple:
            params = ', '.join(str(i) for i in item[1])
            string += f"Query: {item[0]}\nParameters: {params}\n"
        else:
            string += f"Query: {item}\n"
    return string
