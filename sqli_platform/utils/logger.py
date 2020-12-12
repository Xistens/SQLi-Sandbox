#!/usr/bin/python3
import os
import sys
import logging
import time
from logging import handlers
from flask import request


class RequestFormatter(logging.Formatter):
    def format(self, record):
        record.url = request.url_rule
        record.remote_addr = request.remote_addr
        return super(RequestFormatter, self).format(record)

def init_logs(app):
    """
    Initialize the logger

    Reference:
    https://github.com/CTFd/CTFd/blob/master/CTFd/utils/initialization/__init__.py
    """

    logger_mainapp = logging.getLogger("mainapp")
    logger_challenges = logging.getLogger("challenges")

    if not app.debug:
        level = logging.INFO
    else:
        level = logging.DEBUG

    logger_mainapp.setLevel(level)
    logger_challenges.setLevel(level)

    log_dir = app.config["LOG_FOLDER"]
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    logs = {
        "mainapp": os.path.join(log_dir, "mainapp.log"),
        "challenges": os.path.join(log_dir, "challenges.log"),
    }

    try:
        # Create log files if they do not exist
        for log in logs.values():
            if not os.path.exists(log):
                open(log, "a").close()
        
        # https://docs.python.org/3/howto/logging-cookbook.html#using-file-rotation
        mainapp_log = logging.handlers.RotatingFileHandler(
            logs["mainapp"], maxBytes=10485760, backupCount=5
        )
        challenge_log = logging.handlers.RotatingFileHandler(
            logs["challenges"], maxBytes=10485760, backupCount=5
        )

        # formatter = logging.Formatter(
        #     "[%(asctime)s] [%(levelname)s]: %(message)s", "%Y-%m-%d %X")
        formatter = RequestFormatter(
            "%(remote_addr)s - - [%(asctime)s] [%(levelname)s] %(url)s: %(message)s", "%Y-%m-%d %X")
        mainapp_log.setFormatter(formatter)
        challenge_log.setFormatter(formatter)

        logger_mainapp.addHandler(mainapp_log)
        logger_challenges.addHandler(challenge_log)
    except IOError as err:
        raise IOError(err)

    # https://docs.python.org/3/howto/logging-cookbook.html#using-file-rotation
    stdout = logging.StreamHandler(stream=sys.stdout)
    stdout.setFormatter(formatter)

    logger_mainapp.addHandler(stdout)
    logger_challenges.addHandler(stdout)

    # https://docs.python.org/3/library/logging.html#logging.Logger.propagate
    logger_mainapp.propagate = 0
    logger_challenges.propagate = 0


def log_info(logger, fmt, **kwargs):
    """
    Helper function to log INFO messages

    NOT IN USE

    Args:
        logger: (str) Options: mainapp, challenges
        fmt: (str) The format of the message
    """
    props = {
        "date": time.strftime("%m/%d/%Y %X")
    }
    props.update(kwargs)
    logger = logging.getLogger(logger)
    msg = fmt.format(**props)
    logger.info(msg)


