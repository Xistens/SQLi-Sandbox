#!/usr/bin/python3
import fileinput
import hashlib
from flask import (
    url_for,
    redirect,
    session,
    request,
    abort
)
from functools import wraps
from sqli_platform import app, _configs, clog

def hash_pwd(string: str):
    """
    Function to hash password with
    """
    return hashlib.sha256(string.encode("utf-8")).hexdigest()

def get_config(challenge: str, key: str = None):
    """
    Retrieves the flag from the _configs object

    Args:
        challenge:  (str) The name of the challenge to retrieve the flag from
        key:       (str) The name of the configuration to retrieve
    Return:
        Returns the value of the configuration if it is found or, if there is no key, 
        it will return the entire config for the challenge. Otherwise, it will return none.
    """
    for conf in _configs:
        name = conf["config"]["name"]
        if name == challenge:
            if key:
                return conf["config"].get(key, None)
            else:
                return conf["config"]
    return None

def get_flag(challenge: str):
    """
    Retrieves the flag from the _configs object. Abstraction...

    Args:
        challenge:  (str) The name of the challenge to retrieve the flag from
    Return:
        Returns the flag (str) if it is found, else it will return None
    """
    title = get_config(challenge, "title").encode("utf-8")
    key = app.config["flag_key"].encode("utf-8")
    flag_hash = hashlib.md5(key + title).hexdigest()
    flag = app.config["flag_format"].replace("{FLAG}", flag_hash)
    return flag


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


def log_query(data: list):
    """
    Helper function to log SQL queries for challenges

    Args:
        data:   (list) A list containing tuples with the SQL queries and parameters
    """
    if data:
        msg = []
        for d in data:
            msg.append(f"Query: {d[0]}")
            if len(d) > 1:
                msg.append(f"Params: {d[1]}")
        clog.info("\n" + "\n".join(msg))


def format_query(queries: list = []) -> str:
    """
    Helper function to format the database query to display for the user

    Args:
        queries:      (list) A list containing queries or a list containing
                        tuples with queries and input parameters.
    Return:
        string:       (str) The formatted output
    """
    data = []
    for item in queries:
        if type(item) is tuple:
            params = ', '.join(str(i) for i in item[1])
            #string += f"Query: {item[0]}\nParameters: {params}\n"
            data.append((item[0], params))
        else:
            #string += f"Query: {item}\n"
            data.append((item,))
    log_query(data)
    return data


def login_required(bp:str):
    """
    Wrapper for login required. Will redirect traffic to the login page if the
    user is not logged on. The user is considered logged on if a session for the
    blueprint exists with a user id ({BP}_user_id).

    Args:
        bp: (str) Name of the blueprint
    """
    def _login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get(f"{bp}_user_id", None) is None:
                return redirect(url_for(f"{bp}.login", next=request.url))
            return f(*args, **kwargs)
        return decorated_function
    return _login_required


def download_enabled(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        test = app.config["enable_download"]
        if not test:
            abort(404)
            #return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated_function
