from flask import Blueprint, current_app
from flask_restx import Namespace, Resource


"""
Dummy API function for testing
"""

docker_namespace = Namespace(
    "docker", description="Test API"
)

@docker_namespace.route("")
class Docker(Resource):

    def get(self):
        #docker_namespace.logger.warning('TEST WARNING')
        return {"success": True, "data": "test"}
