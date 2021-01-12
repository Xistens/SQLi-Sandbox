from flask import Blueprint, current_app, jsonify
from flask_restx import Namespace, Resource
from sqli_platform import _configs
from sqli_platform.utils.challenge import get_flag

"""
Dummy API function for testing
"""

flags_namespace = Namespace(
    "getFlags", description="Get all flags"
)

@flags_namespace.route("")
class Flags(Resource):


    def get_flags(self):
        flags = {}
        for conf in _configs:
            name = conf["config"]["name"]
            flags[name] = get_flag(name)
        return flags

    def get(self):
        return jsonify(self.get_flags())
