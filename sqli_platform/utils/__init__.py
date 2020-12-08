#!/usr/bin/python3
import os
import json
import importlib


def load_json(path:str):
    """
    Loads JSON data into memory

    TODO:
        - Change behaviour on IOError?
    """
    try:
        with open(path, "r") as fd:
            return json.load(fd)
    except IOError:
        raise IOError(f"Failed to open {path}")


def get_directories(path: str, blacklist: list = ["__pycache__"]) -> list:
    """
    This functions returns a list of all directories from a specified path, 
    but ignores all folders in the blacklist.

    Args:
        path: (str) Path to the directory to retrieve all folders from
        blacklist: (list) Names to ignore while building the list
    Return:
        dirs: (list) List of directories inside the specified path
    """
    dirs = []
    for directory in os.listdir(path):
        if directory in blacklist:
            continue
        if os.path.isdir(os.path.join(path, directory)):
            dirs.append(directory)
    return dirs


def get_challenge_configs(path: str, config: str) -> list:
    """
    Loads all configs from challenges into memory to be used 
    to dynamically load blueprints.

    Get all sub-directories from the challenges folder, 
    check if config.json exists and load it into memory.
    Args:
        path:   (str) Path to challenges directory
        config: (str) Name of the config file
    Return:
        blueprints: (list) List of all the blueprints from the challenges

    TODO:
        - Check if config file is correct / error handling
    """
    root = f".{path.split('/')[-1]}"

    configs = []
    # Get all sub-directories / challenges
    challenges = get_directories(f"{path}")
    for c in challenges:
        # Path to config file
        tmp_path = f"{path}/{c}/{config}"
        if os.path.isfile(f'{tmp_path}'):
            data = load_json(tmp_path)

            # Check if challenge is enabled or not
            enabled = data.get("enabled", True)
            if enabled:
                configs.append({
                    "path": f"{root}.{c}",
                    "config": data
                })
    return configs


def load_blueprints(app, limiter, configs: list):
    """
    Imports challenges modules and registers their blueprints

    Imports each module into the context of sqli_platform (sqli_platform acts as the anchor),
    then registers the blueprints from that module

    Args:
        app:        (flask.app.Flask)
        limiter:    (class 'flask_limiter.extension.Limiter')
        configs:    (list) List containing configurations of all challenges

    TODO:
        - Add error handling?
    """
    for conf in configs:
        module = importlib.import_module(
            f"{conf['path']}.views", package="sqli_platform")
        
        # Get blueprint
        bp = getattr(module, conf["config"]["name"])

        if "limiter" in conf["config"]:
            limiter.limit(conf["config"]["limiter"])(bp)
        app.register_blueprint(bp)

