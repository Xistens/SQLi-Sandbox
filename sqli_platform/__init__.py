#!/usr/bin/python3
import os
import logging
import sqli_platform.utils as utils
import sqli_platform.utils.logger as logger
from flask import Flask, g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

_basedir = os.path.abspath(os.path.dirname(__file__))

# Path to challenges
_challenges_path = f'{_basedir}/challenges'

# Name of the config file for a challenge
_challenge_config = 'config.json'

app = Flask(__name__)
app.debug = True
# Change me
app.secret_key = b"dummy_key"
limiter = Limiter(app, default_limits=[], key_func=get_remote_address)

# Temp logging directory, remember to change?
app.config['LOG_FOLDER'] = f'{_basedir}/logs'
#app.config['LOG_FILE'] = f'{_basedir}/logs/application.log'

# Configure logging
logger.init_logs(app)
app_log = logging.getLogger("mainapp")
app_log.debug("Initializing loggers")

# Load configs from all challenges into memory
_configs = utils.get_challenge_configs(_challenges_path, _challenge_config)

# Create MySQL databases for all the challenges and set full permission
from sqli_platform import database

db = database.Database(app, _configs, _basedir)

# Register the API
from sqli_platform.api import api
app.register_blueprint(api)

# Import challenges modules and register their blueprints
utils.load_blueprints(app, limiter, _configs)


from sqli_platform import routes

