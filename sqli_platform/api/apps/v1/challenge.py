#!/usr/bin/python3
from sqli_platform import app, app_log, socketio
from flask_socketio import send, emit


@socketio.on('get_query')
def send_query(data):
    print("SEnd DATatatata")
    emit("message_from_server", {'text':'Msg reveiced!'})