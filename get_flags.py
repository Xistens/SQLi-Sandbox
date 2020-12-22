#!/usr/bin/python3
import json
import sqli_platform.utils as utils
from sqli_platform import app
from sqli_platform.utils.challenge import get_flag
from sqli_platform import _challenges_path, _challenge_config

_configs = utils.get_challenge_configs(_challenges_path, _challenge_config)

def get_flags(configs: dict):
    flags = {}
    for conf in configs:
        name = conf["config"]["name"]
        flags[name] = get_flag(name)
    return flags

flags = get_flags(_configs)
print(json.dumps(flags, indent=4, sort_keys=True))
