from flask import Blueprint, current_app
from flask_restx import Api

from sqli_platform.api.apps.v1.flags import flags_namespace

"""
Testing API... might not be needed
"""

api = Blueprint("api", __name__, url_prefix="/api/v1")
API_V1 = Api(api, version="v1")

API_V1.add_namespace(flags_namespace, "/getFlags")
