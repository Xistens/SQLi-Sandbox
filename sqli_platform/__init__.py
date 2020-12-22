#!/usr/bin/python3
import os
import logging
import sqli_platform.utils as utils
import sqli_platform.utils.logger as logger
from flask import Flask, g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

_basedir = os.path.abspath(os.path.dirname(__file__))
DOWNLOAD_PATH = f"{_basedir}/../scripts/"
DOWNLOAD_WHITELIST = ["challenge3", "challenge4"]
# Path to challenges
_challenges_path = f'{_basedir}/challenges'

# Name of the config file for a challenge
_challenge_config = 'config.json'


app = Flask(__name__)
app.debug = True

# Change me
app.secret_key = b"dummy_key"
app.config.update(
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",

    JSONIFY_PRETTYPRINT_REGULAR = True,
    # Enable/disable debug and guidance for the entire app
    enable_debug_query = True,
    enable_guidance = True,
    
    # Default value for debug and guidance setting (enabled/disabled)
    debug_query_default = True,
    guidance_default = False,

    # Enable/disable download page for extra material
    enable_download = True,

    flag_key = "xV6WxVghQ7fFxarqnyj5EYwPmrGZgt4Q",
    # "{FLAG}" will be replaced with the MD5 sum of challenge title and flag_key
    flag_format = "THM{{FLAG}}",

    LOG_FOLDER = f'{_basedir}/logs',

)


limiter = Limiter(app, default_limits=[], key_func=get_remote_address)


# Configure logging
logger.init_logs(app)
app_log = logging.getLogger("mainapp")
clog = logging.getLogger("challenges")
app_log.debug("Initializing loggers")

# Load configs from all challenges into memory
_configs = utils.get_challenge_configs(_challenges_path, _challenge_config)


# Register the API if in debug mode
if app.debug:
    from sqli_platform.api import api
    app.register_blueprint(api)

from sqli_platform import database
db = database.Database(app, _configs, _basedir)

# Import challenges modules and register their blueprints
utils.load_blueprints(app, limiter, _configs)

from sqli_platform import routes

